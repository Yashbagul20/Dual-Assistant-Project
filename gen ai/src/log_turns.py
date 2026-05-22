# append chat turns to logs/assistant.jsonl for debugging
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

log = logging.getLogger("assistants")
if not log.handlers:
    h = logging.FileHandler(LOG_DIR / "assistant.jsonl", encoding="utf-8")
    h.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(h)
    log.setLevel(logging.INFO)


def log_turn(assistant, user_message, response, latency_ms, blocked=False, model_id=""):
    log.info(json.dumps({
        "ts": datetime.now(timezone.utc).isoformat(),
        "assistant": assistant,
        "model": model_id,
        "user": user_message[:500],
        "reply": response[:1000],
        "ms": latency_ms,
        "blocked": blocked,
    }))
