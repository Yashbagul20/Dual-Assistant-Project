"""
Modal deploy for Qwen2.5-0.5B-Instruct
Run from repo root: modal deploy deploy/modal/serve.py
"""
import sys
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "torch", "transformers>=4.44", "accelerate", "sentencepiece"
)
app = modal.App("oss-qwen-assistant", image=image)
MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"


@app.cls(gpu="T4", container_idle_timeout=300, allow_concurrent_inputs=10)
class QwenOSS:
    @modal.enter()
    def load(self):
        from deploy.common.oss_engine import OSSChatEngine
        self.engine = OSSChatEngine(MODEL_ID, platform="modal")

    @modal.method()
    def chat(self, message: str):
        return self.engine.chat(message)


@app.local_entrypoint()
def test(prompt: str = "Hello, one sentence reply."):
    print(QwenOSS().chat.remote(prompt))
