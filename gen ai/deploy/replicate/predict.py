"""
Replicate / Cog predictor for Qwen OSS assistant
"""
from cog import BasePredictor, Input
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from deploy.common.oss_engine import OSSChatEngine


class Predictor(BasePredictor):
    def setup(self):
        self.engine = OSSChatEngine(
            os.environ.get("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct"),
            platform="replicate",
        )
        self.engine.load()

    def predict(self, message: str = Input(description="User message")) -> dict:
        return self.engine.chat(message)
