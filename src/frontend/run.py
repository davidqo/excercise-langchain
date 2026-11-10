import json
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"


def load_config() -> dict:
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    cfg = load_config()
    server_cfg = cfg["server"]

    command = [
        sys.executable,
        "-m",
        "chainlit",
        "run",
        str(SCRIPT_DIR / "app.py"),
        "--host",
        server_cfg["host"],
        "--port",
        str(server_cfg["port"]),
    ]
    return subprocess.call(command, cwd=SCRIPT_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
