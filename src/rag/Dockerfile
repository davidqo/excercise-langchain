FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY src/rag/requirements.txt .
RUN uv venv --link-mode=copy
RUN uv pip install -r requirements.txt --link-mode=copy

COPY src/rag/search_service.py .
COPY src/rag/config.json .

CMD [".venv/bin/python", "search_service.py"]
