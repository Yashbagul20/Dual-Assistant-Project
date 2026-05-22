import json
import time
from datetime import datetime, timezone
from pathlib import Path

LOG_ROOT = Path(__file__).resolve().parents[2] / "logs"


def _write(path, record):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_chat(platform, user_msg, reply, ms, blocked=False, model=""):
    _write(LOG_ROOT / "deploy_chat.jsonl", {
        "ts": datetime.now(timezone.utc).isoformat(),
        "platform": platform,
        "model": model,
        "user": user_msg[:400],
        "reply": reply[:800],
        "latency_ms": ms,
        "blocked": blocked,
    })


def log_latency(platform, cold_start_ms, inference_ms):
    _write(LOG_ROOT / "deploy_latency.jsonl", {
        "ts": datetime.now(timezone.utc).isoformat(),
        "platform": platform,
        "cold_start_ms": cold_start_ms,
        "inference_ms": inference_ms,
    })


class Timer:
    def __init__(self):
        self.t0 = time.perf_counter()

    def ms(self):
        return (time.perf_counter() - self.t0) * 1000
