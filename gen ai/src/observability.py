# observability — jsonl logs for chat, eval, deploy benchmarks
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def _append(filename, record):
    with (LOG_DIR / filename).open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_turn(assistant, user_message, response, latency_ms, blocked=False, model_id=""):
    _append("assistant.jsonl", {
        "ts": datetime.now(timezone.utc).isoformat(),
        "assistant": assistant,
        "model": model_id,
        "user": user_message[:500],
        "reply": response[:1000],
        "ms": latency_ms,
        "blocked": blocked,
    })


def log_eval_run(summary_path, row_count):
    _append("eval_events.jsonl", {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": "eval_complete",
        "summary": str(summary_path),
        "rows": row_count,
    })


def log_deploy_bench(platform, cold_ms, infer_ms, model_id):
    _append("deploy_latency.jsonl", {
        "ts": datetime.now(timezone.utc).isoformat(),
        "platform": platform,
        "cold_start_ms": cold_ms,
        "inference_ms": infer_ms,
        "model": model_id,
    })
