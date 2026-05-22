"""
RunPod serverless handler — Qwen2.5-0.5B-Instruct
Input: {"message": "hello", "session_id": "optional"}
"""
import runpod
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from deploy.common.oss_engine import OSSChatEngine

engines = {}


def get_engine(sid="default"):
    if sid not in engines:
        engines[sid] = OSSChatEngine(platform="runpod")
    return engines[sid]


def handler(event):
    inp = event.get("input", {})
    msg = inp.get("message", "")
    sid = inp.get("session_id", "default")
    if inp.get("reset"):
        get_engine(sid).memory.clear()
        return {"text": "session cleared", "latency_ms": 0}
    return get_engine(sid).chat(msg)


runpod.serverless.start({"handler": handler})
