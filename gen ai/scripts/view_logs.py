# quick log viewer
import json
from pathlib import Path
from collections import Counter

root = Path(__file__).resolve().parents[1]
logs = root / "logs"

for name in ["assistant.jsonl", "deploy_chat.jsonl", "deploy_latency.jsonl", "eval_events.jsonl"]:
    p = logs / name
    if not p.exists():
        print(f"{name}: (no file yet)")
        continue
    lines = p.read_text(encoding="utf-8").strip().splitlines()
    print(f"\n{name} — {len(lines)} events")
    if name == "assistant.jsonl" and lines:
        bots = Counter(json.loads(x).get("assistant") for x in lines[-20:])
        print("  last 20 by assistant:", dict(bots))
    if name == "deploy_latency.jsonl" and lines:
        last = json.loads(lines[-1])
        print(f"  last: {last.get('platform')} infer={last.get('inference_ms')}ms")
