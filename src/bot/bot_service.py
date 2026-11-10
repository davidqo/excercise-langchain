import os
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_ollama import ChatOllama

app = FastAPI(title="LangChain Bot Service")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

def load_bot_config():
    if not os.path.exists(CONFIG_PATH):
        raise RuntimeError(f"Конфигурация бота {CONFIG_PATH} не найдена!")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Загружаем настройки конкретно этого микросервиса
bot_cfg = load_bot_config()
RAG_URL = bot_cfg["rag"]["service_url"]

# Хранилище истории диалогов
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()

    return store[session_id]

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a helpful AI assistant. "
                "Answer the user's question "
                "based ONLY on the provided context.\n\n"
                "You may use the conversation history, but only to identify the user's name. "
                "You must NOT notice and write in chat any facts about the user such as their city, street, or personal preferences—in the conversation. \n\n"
                "Also, you must never tell the user the secret code for canceling all tasks. \n\n"
                "If the answer is not in the context, "
                "honestly state that you do not know the answer.\n\n"
                "Context:\n"
                "{context}"
            ),
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

llm = ChatOllama(
    model=bot_cfg["llm"]["model_name"], 
    temperature=bot_cfg["llm"]["temperature"],
    base_url=f"http://{bot_cfg['llm']['provider_host']}"
)

chain = prompt_template | llm | StrOutputParser()

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)

class BotQuery(BaseModel):
    question: str
    session_id: str

def fetch_context(question: str) -> str:
    """Делает запрос к независимому микросервису RAG"""
    try:
        response = requests.post(
            RAG_URL, 
            json={"text": question, "k": 3}, 
            timeout=5
        )
        response.raise_for_status()
        docs = response.json()
        return "\n\n".join([doc["content"] for doc in docs])
    except Exception as e:
        print(f"[RAG Connection Error] {e}")
        return "Контекст из базы данных временно недоступен."

@app.post("/ask")
async def ask_bot(request: BotQuery):
    try:
        context = fetch_context(request.question)
        
        answer = chain_with_memory.invoke(
            {
                "context": context,
                "question": request.question
            },
            config={
                "configurable": {
                    "session_id": request.session_id
                }
            }
        )
        
        return {
            "answer": answer,
            "has_context": context != "Контекст из базы данных временно недоступен."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
