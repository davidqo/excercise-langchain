# excercise-langchain

RAG demo with three services: search API, bot API, and Chainlit web UI.

## Requirements

- Docker and Docker Compose
- Python 3.11 with `uv` for local document indexing
- Local Ollama-compatible LLM. Configure it in `src/bot/config.json`:
  - `llm.provider_host`, for example `127.0.0.1:11434`
  - `llm.model_name`, for example `local-qwen`

## Index Documents

Put `.txt` files into `documents/`, then build the Chroma index:

```bash
uv venv
uv pip install -r src/rag/requirements.txt
./index_documents.sh
```

The first indexing run can download the embedding model into `.cache/huggingface`.

## Run

```bash
./start.sh
```

Open the UI at http://127.0.0.1:8000.

Default service ports:

- RAG API: `127.0.0.1:8080`
- Bot API: `127.0.0.1:8081`
- Web UI: `127.0.0.1:8000`

Service settings live in `src/rag/config.json`, `src/bot/config.json`, and `src/frontend/config.json`.
