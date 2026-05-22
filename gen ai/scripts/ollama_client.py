# chat with local ollama + same guardrails/tools/memory as cloud deploy
import json
import re
import urllib.request

import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from src.guardrails import safety
from src.tools.builtin_tools import run_tool_if_needed
from src.memory.conversation_memory import ConversationMemory
from src.assistants.base import SYSTEM_PROMPT

OLLAMA = "http://localhost:11434/api/chat"
MODEL = "qwen-assistant"


def ollama_chat(messages):
    body = json.dumps({"model": MODEL, "messages": messages, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())["message"]["content"]


def main():
    mem = ConversationMemory(max_turns=10, system_prompt=SYSTEM_PROMPT)
    print("ollama client (guardrails+tools). empty line to quit.")
    while True:
        q = input("\nYou: ").strip()
        if not q:
            break
        br = safety.bias_safe_response(q)
        if br:
            print("Bot:", br)
            continue
        chk = safety.check_input(q)
        if chk.action == safety.SafetyAction.BLOCK_INPUT:
            print("Bot: blocked -", chk.reason)
            continue
        extra = run_tool_if_needed(q)
        user = q + (f"\n[tool]\n{extra}" if extra else "")
        mem.add("user", q)
        msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
        for m in mem.messages:
            role = "assistant" if m.role == "assistant" else "user"
            msgs.append({"role": role, "content": m.content if m.role != "user" else user})
        reply = ollama_chat(msgs)
        out = safety.check_output(reply, q)
        reply = out.sanitized_text
        mem.add("assistant", reply)
        print("Bot:", reply)


if __name__ == "__main__":
    main()
