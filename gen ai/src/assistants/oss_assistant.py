import os
import time

from src.assistants.base import AssistantResponse, BaseAssistant
from src.guardrails.safety import SafetyAction, bias_safe_response, check_input, check_output
from src.observability import log_turn
from src.tools.builtin_tools import run_tool_if_needed

# learned the hard way: Qwen 0.5B isn't on HF inference API
HF_FALLBACKS = ["HuggingFaceTB/SmolLM2-1.7B-Instruct", "meta-llama/Llama-3.2-1B-Instruct"]


class OSSAssistant(BaseAssistant):
    name = "oss"
    model_id = os.getenv("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")

    def __init__(self, max_turns=10):
        super().__init__(max_turns)
        self.pipeline = None
        self.hf_token = os.getenv("HF_TOKEN", "")
        self.backend = self._pick_backend()

    def _pick_backend(self):
        b = os.getenv("OSS_BACKEND", "").lower().strip()
        if b in ("groq", "local", "hf"):
            return b
        if os.getenv("USE_HF_INFERENCE", "").lower() == "true":
            return "hf"
        if os.getenv("GROQ_API_KEY"):
            return "groq"  # easiest when you already have groq key
        return "local"

    def _run_groq(self, msgs):
        from groq import Groq
        model = os.getenv("OSS_GROQ_MODEL", "llama-3.1-8b-instant")
        client = Groq(api_key=os.environ["GROQ_API_KEY"])
        r = client.chat.completions.create(model=model, messages=msgs, temperature=0.7, max_tokens=512)
        self.model_id = model
        return r.choices[0].message.content or ""

    def _run_hf(self, msgs):
        from huggingface_hub import InferenceClient
        client = InferenceClient(token=self.hf_token or None)
        for mid in [self.model_id] + HF_FALLBACKS:
            try:
                r = client.chat_completion(messages=msgs, model=mid, max_tokens=256)
                self.model_id = mid
                return r.choices[0].message.content.strip()
            except Exception as e:
                last = e
        raise last

    def _run_local(self, prompt):
        if self.pipeline is None:
            from transformers import pipeline
            self.pipeline = pipeline("text-generation", model=self.model_id, device_map="auto", torch_dtype="auto")
        out = self.pipeline(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, return_full_text=False)
        return out[0]["generated_text"].strip()

    def _msgs(self, text):
        m = self.memory.to_openai_format()
        if m and m[-1]["role"] == "user":
            m[-1]["content"] = text
        return m

    def chat(self, user_message):
        t0 = time.perf_counter()

        canned = bias_safe_response(user_message)
        if canned:
            self.memory.add("user", user_message)
            self.memory.add("assistant", canned)
            return AssistantResponse(canned, latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id)

        safety = check_input(user_message)
        if safety.action == SafetyAction.BLOCK_INPUT:
            return AssistantResponse("blocked", blocked=True, block_reason=safety.reason,
                                     latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id)

        extra = run_tool_if_needed(user_message)
        prompt = user_message + ("\n\n[tool]\n" + extra if extra else "")
        self.memory.add("user", user_message)

        try:
            if self.backend == "groq":
                raw = self._run_groq(self._msgs(prompt))
            elif self.backend == "hf":
                raw = self._run_hf(self._msgs(prompt))
            else:
                hist = self.memory.to_chat_text()
                full = f"{hist}\nUser: {prompt}\nAssistant:" if hist else f"System: {self.memory.system_prompt}\nUser: {prompt}\nAssistant:"
                raw = self._run_local(full)
        except Exception as e:
            return AssistantResponse(
                f"oss failed ({self.backend}): {e} — try OSS_BACKEND=groq in .env",
                latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id,
            )

        out = check_output(raw, user_message)
        text = out.sanitized_text if out.action == SafetyAction.REFUSE_OUTPUT else raw
        self.memory.add("assistant", text)
        resp = AssistantResponse(text, blocked=(out.action == SafetyAction.REFUSE_OUTPUT),
                                 latency_ms=(time.perf_counter()-t0)*1000, model_id=self.model_id)
        log_turn("oss", user_message, resp.text, resp.latency_ms, resp.blocked, resp.model_id)
        return resp
