FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app

COPY src/frontend/requirements.txt .
RUN uv venv --link-mode=copy
RUN uv pip install -r requirements.txt --link-mode=copy

COPY src/frontend/app.py .
COPY src/frontend/run.py .
COPY src/frontend/config.json .
COPY src/frontend/.chainlit ./.chainlit
COPY src/frontend/public ./public

CMD [".venv/bin/python", "run.py"]
