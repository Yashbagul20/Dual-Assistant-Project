# benchmark OSS latency (local Qwen or groq backend from .env)
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
load_dotenv(root / ".env")

from src.assistants.oss_assistant import OSSAssistant
from src.observability import log_deploy_bench

PROMPTS = ["Hello", "What is 2+2?", "What time is it"]


def main():
    platform = "local-groq" if __import__("os").getenv("OSS_BACKEND") == "groq" else "local"
    bot = OSSAssistant()
    print(f"benchmarking OSS backend={bot.backend} model={bot.model_id}")

    times = []
    for i, p in enumerate(PROMPTS):
        t0 = time.perf_counter()
        r = bot.chat(p)
        ms = time.perf_counter() - t0
        times.append(ms * 1000)
        print(f"  [{i+1}] {ms*1000:.0f}ms blocked={r.blocked} -> {r.text[:60]}...")

    avg = sum(times) / len(times)
    log_deploy_bench(platform, 0, avg, bot.model_id)
    print(f"\navg latency: {avg:.0f} ms (logged to logs/deploy_latency.jsonl)")


if __name__ == "__main__":
    main()
