#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ -x "$PROJECT_DIR/.venv/bin/python" ]]; then
  PYTHON="$PROJECT_DIR/.venv/bin/python"
elif [[ -x "$PROJECT_DIR/.venv/Scripts/python.exe" ]]; then
  PYTHON="$PROJECT_DIR/.venv/Scripts/python.exe"
else
  echo "Project Python not found. Create it first, for example: python3 -m venv .venv" >&2
  exit 1
fi

exec "$PYTHON" "$PROJECT_DIR/src/rag/index_cli.py" "$@"