import os
import time

from lib.memory import ChatMemory
from lib import safety, tools, metrics

SYSTEM = (
    "You are a helpful open-source assistant. Be concise. "
    "Refuse illegal or harmful requests."
)


class OSSChatEngine:
    def __init__(self, model_id=None, max_turns=10):
        self.model_id = model_id or os.getenv("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
        self.memory = ChatMemory(max_turns=max_turns, system=SYSTEM)
        self._pipe = None

    def load(self):
        if self._pipe:
            return
        from transformers import pipeline
        self._pipe = pipeline(
            "text-generation", model=self.model_id, device_map="auto", torch_dtype="auto"
        )

    def chat(self, user_message):
        t0 = time.perf_counter()

        br = safety.bias_reply(user_message)
        if br:
            self.memory.add("user", user_message)
            self.memory.add("assistant", br)
            ms = (time.perf_counter() - t0) * 1000
            metrics.log_chat(user_message, br, ms, model=self.model_id)
            return br, ms, False, False

        blocked, _ = safety.check_input(user_message)
        if blocked:
            msg = "Request blocked by safety layer."
            ms = (time.perf_counter() - t0) * 1000
            metrics.log_chat(user_message, msg, ms, blocked=True, model=self.model_id)
            return msg, ms, True, False

        tool_out = tools.run_tools(user_message)
        prompt_user = user_message
        used_tool = False
        if tool_out:
            used_tool = True
            prompt_user = f"{user_message}\n[tool: {tool_out}]"

        self.memory.add("user", user_message)
        self.load()
        prompt = self.memory.prompt_block().replace(f"User: {user_message}", f"User: {prompt_user}", 1)
        out = self._pipe(prompt, max_new_tokens=220, do_sample=True, temperature=0.7, return_full_text=False)
        raw = out[0]["generated_text"].strip()
        final = safety.check_output(raw, user_message)
        self.memory.add("assistant", final)
        ms = (time.perf_counter() - t0) * 1000
        metrics.log_chat(user_message, final, ms, model=self.model_id, tools=used_tool)
        return final, ms, False, used_tool
