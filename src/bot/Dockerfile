FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app

COPY src/bot/requirements.txt .
RUN uv venv --link-mode=copy
RUN uv pip install -r requirements.txt --link-mode=copy

COPY src/bot/bot_service.py .
COPY src/bot/config.json .

CMD [".venv/bin/python", "bot_service.py"]
