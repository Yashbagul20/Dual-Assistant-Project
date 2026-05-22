import os
import time

from groq import Groq

from src.assistants.base import AssistantResponse, BaseAssistant
from src.guardrails.safety import SafetyAction, bias_safe_response, check_input, check_output
from src.observability import log_turn
from src.tools.builtin_tools import run_tool_if_needed


class FrontierAssistant(BaseAssistant):
    name = "frontier"
    model_id = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    def __init__(self, max_turns=10):
        super().__init__(max_turns)
        key = os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("missing GROQ_API_KEY in .env")
        self.client = Groq(api_key=key)

    def chat(self, user_message):
        t0 = time.perf_counter()

        canned = bias_safe_response(user_message)
        if canned:
            self.memory.add("user", user_message)
            self.memory.add("assistant", canned)
            return AssistantResponse(canned, latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id)

        safety = check_input(user_message)
        if safety.action == SafetyAction.BLOCK_INPUT:
            return AssistantResponse(
                "blocked by safety filter",
                blocked=True, block_reason=safety.reason,
                latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id,
            )

        extra = run_tool_if_needed(user_message)
        prompt = user_message
        if extra:
            prompt = user_message + "\n\n[tool]\n" + extra

        self.memory.add("user", user_message)
        msgs = self.memory.to_openai_format()
        if msgs and msgs[-1]["role"] == "user":
            msgs[-1]["content"] = prompt

        try:
            r = self.client.chat.completions.create(
                model=self.model_id, messages=msgs, temperature=0.7, max_tokens=512,
            )
            raw = r.choices[0].message.content or ""
        except Exception as e:
            return AssistantResponse(f"groq error: {e}", latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id)

        out = check_output(raw, user_message)
        text = out.sanitized_text if out.action == SafetyAction.REFUSE_OUTPUT else raw
        self.memory.add("assistant", text)

        resp = AssistantResponse(
            text, blocked=(out.action == SafetyAction.REFUSE_OUTPUT), block_reason=out.reason,
            latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id,
        )
        log_turn("frontier", user_message, resp.text, resp.latency_ms, resp.blocked, resp.model_id)
        return resp
