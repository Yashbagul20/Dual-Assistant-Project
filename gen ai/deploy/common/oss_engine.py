import os
import time

from .memory import ChatMemory
from . import safety, tools, metrics

SYSTEM = (
    "You are a helpful open-source assistant. Be concise. "
    "Refuse illegal or harmful requests. Say when unsure."
)


class OSSChatEngine:
    """Qwen (or any HF causal LM) with memory, guardrails, tools — for public deploy."""

    def __init__(self, model_id=None, platform="local", max_turns=10):
        self.model_id = model_id or os.getenv("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
        self.platform = platform
        self.memory = ChatMemory(max_turns=max_turns, system=SYSTEM)
        self._pipe = None
        self._cold_ms = 0

    def load(self):
        if self._pipe:
            return
        t = metrics.Timer()
        from transformers import pipeline
        self._pipe = pipeline(
            "text-generation",
            model=self.model_id,
            device_map="auto",
            torch_dtype="auto",
        )
        self._cold_ms = t.ms()
        metrics.log_latency(self.platform, self._cold_ms, 0)

    def chat(self, user_message):
        t = metrics.Timer()

        br = safety.bias_reply(user_message)
        if br:
            self.memory.add("user", user_message)
            self.memory.add("assistant", br)
            metrics.log_chat(self.platform, user_message, br, t.ms(), model=self.model_id)
            return {"text": br, "blocked": False, "latency_ms": t.ms(), "tools_used": False}

        blocked, reason = safety.check_input(user_message)
        if blocked:
            msg = "Request blocked by safety layer."
            metrics.log_chat(self.platform, user_message, msg, t.ms(), blocked=True, model=self.model_id)
            return {"text": msg, "blocked": True, "reason": reason, "latency_ms": t.ms()}

        tool_out = tools.run_tools(user_message)
        prompt_user = user_message
        tools_used = False
        if tool_out:
            tools_used = True
            prompt_user = f"{user_message}\n[tool output: {tool_out}]"

        self.memory.add("user", user_message)
        self.load()
        prompt = self.memory.prompt_block().replace(
            f"User: {user_message}",
            f"User: {prompt_user}",
            1,
        )

        out = self._pipe(
            prompt,
            max_new_tokens=220,
            do_sample=True,
            temperature=0.7,
            return_full_text=False,
        )
        raw = out[0]["generated_text"].strip()
        final = safety.check_output(raw, user_message)
        self.memory.add("assistant", final)

        infer_ms = t.ms()
        metrics.log_latency(self.platform, self._cold_ms, infer_ms)
        metrics.log_chat(self.platform, user_message, final, infer_ms, model=self.model_id)

        return {
            "text": final,
            "blocked": False,
            "latency_ms": infer_ms,
            "cold_start_ms": self._cold_ms,
            "tools_used": tools_used,
            "model": self.model_id,
        }
