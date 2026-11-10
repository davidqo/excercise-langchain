import asyncio
import os
import time
import uuid
from pathlib import Path
from typing import Any

import chainlit as cl
import httpx
from chainlit.input_widget import Select, Slider, Switch


BOT_API_URL = os.getenv("BOT_API_URL", "http://127.0.0.1:8081/ask")
RAG_API_URL = os.getenv("RAG_API_URL", "http://127.0.0.1:8080/search")
HTTP_TIMEOUT = float(os.getenv("FRONTEND_HTTP_TIMEOUT", "180"))


def default_settings() -> dict[str, Any]:
    return {
        "show_sources": True,
        "show_stats": True,
        "show_history": False,
        "rag_k": 3,
        "appearance": "Comfortable",
    }


def get_settings() -> dict[str, Any]:
    settings = default_settings()
    settings.update(cl.user_session.get("settings") or {})
    return settings


async def send_settings() -> None:
    settings = get_settings()
    await cl.ChatSettings(
        [
            Switch(
                id="show_sources",
                label="Show RAG sources",
                initial=settings["show_sources"],
            ),
            Switch(
                id="show_stats",
                label="Show bot diagnostics",
                initial=settings["show_stats"],
            ),
            Switch(
                id="show_history",
                label="Show session history widget",
                initial=settings["show_history"],
            ),
            Slider(
                id="rag_k",
                label="Source documents",
                initial=settings["rag_k"],
                min=1,
                max=5,
                step=1,
            ),
            Select(
                id="appearance",
                label="Interface density",
                values=["Compact", "Comfortable", "Spacious"],
                initial_index=["Compact", "Comfortable", "Spacious"].index(
                    settings["appearance"]
                ),
            ),
        ]
    ).send()


async def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any] | list[Any]:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


def get_bot_session_id() -> str:
    session_id = cl.user_session.get("bot_session_id")
    if not session_id:
        session_id = cl.user_session.get("id") or str(uuid.uuid4())
        cl.user_session.set("bot_session_id", session_id)
    return str(session_id)


async def ask_bot(question: str, session_id: str) -> dict[str, Any]:
    data = await post_json(
        BOT_API_URL,
        {
            "question": question,
            "session_id": session_id,
        },
    )
    if not isinstance(data, dict):
        raise ValueError("Bot API returned an unexpected response")
    return data


async def fetch_sources(question: str, k: int) -> list[dict[str, Any]]:
    data = await post_json(RAG_API_URL, {"text": question, "k": k})
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def normalize_sources(raw_sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for index, source in enumerate(raw_sources, start=1):
        metadata = source.get("metadata") or {}
        source_name = (
            metadata.get("source")
            or metadata.get("file")
            or metadata.get("path")
            or metadata.get("filename")
            or f"Document {index}"
        )
        title = Path(str(source_name)).name
        safe_metadata = {
            key: Path(str(value)).name
            if key in {"source", "file", "path", "filename"}
            else value
            for key, value in metadata.items()
        }
        normalized.append(
            {
                "title": title,
                "metadata": safe_metadata,
            }
        )
    return normalized


def append_history(role: str, content: str) -> list[dict[str, str]]:
    history = cl.user_session.get("history") or []
    history.append({"role": role, "content": content})
    cl.user_session.set("history", history)
    return history


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("history", [])
    cl.user_session.set("settings", default_settings())
    await send_settings()
    await cl.Message(
        content="Ask a question. I will call the existing bot API and show RAG details when enabled."
    ).send()


@cl.on_settings_update
async def on_settings_update(settings: dict[str, Any]) -> None:
    merged = default_settings()
    merged.update(settings)
    merged["rag_k"] = int(merged.get("rag_k") or 3)
    cl.user_session.set("settings", merged)
    await cl.Message(content="Interface settings updated.").send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    question = message.content.strip()
    if not question:
        await cl.Message(content="Please send a non-empty question.").send()
        return

    settings = get_settings()
    session_id = get_bot_session_id()
    append_history("user", question)

    started = time.perf_counter()
    async with cl.Step(name="Calling bot_service", type="tool") as step:
        step.input = question
        bot_task = ask_bot(question, session_id)
        source_task = fetch_sources(question, int(settings["rag_k"]))
        bot_response, raw_sources = await asyncio.gather(bot_task, source_task)
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        step.output = f"Received answer and {len(raw_sources)} source documents in {elapsed_ms} ms."

    answer = str(bot_response.get("answer") or "The bot returned an empty answer.")
    has_context = bool(bot_response.get("has_context"))
    sources = normalize_sources(raw_sources)
    history = append_history("assistant", answer)

    elements: list[cl.Element] = []
    if settings["show_stats"]:
        elements.append(
            cl.CustomElement(
                name="BotStats",
                props={
                    "elapsedMs": elapsed_ms,
                    "hasContext": has_context,
                    "sourceCount": len(sources),
                    "messageCount": len(history),
                    "appearance": settings["appearance"],
                },
                display="inline",
            )
        )
    if settings["show_sources"] and sources:
        elements.append(
            cl.CustomElement(
                name="RagSources",
                props={"sources": sources, "appearance": settings["appearance"]},
                display="inline",
            )
        )
    if settings["show_history"]:
        elements.append(
            cl.CustomElement(
                name="SessionHistory",
                props={
                    "items": history[-8:],
                    "appearance": settings["appearance"],
                },
                display="inline",
            )
        )

    await cl.Message(content=answer, elements=elements).send()
