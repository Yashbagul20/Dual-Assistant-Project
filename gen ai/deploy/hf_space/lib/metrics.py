import json
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("/tmp/oss_logs")
LOG_DIR.mkdir(exist_ok=True)


def log_chat(user_msg, reply, ms, blocked=False, model="", tools=False):
    rec = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "platform": "hf_space",
        "model": model,
        "user": user_msg[:400],
        "reply": reply[:800],
        "latency_ms": ms,
        "blocked": blocked,
        "tools_used": tools,
    }
    with (LOG_DIR / "chat.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
