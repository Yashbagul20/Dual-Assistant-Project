from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: str


class ConversationMemory:
    # keeps last N back-and-forth turns (+ system prompt when exporting)
    def __init__(self, max_turns=10, system_prompt=""):
        self.max_turns = max_turns
        self.system_prompt = system_prompt
        self.messages = []

    def add(self, role, content):
        self.messages.append(Message(role, content))
        # drop old stuff so we don't blow the context window
        non_sys = [m for m in self.messages if m.role != "system"]
        if len(non_sys) > self.max_turns * 2:
            self.messages = non_sys[-(self.max_turns * 2):]

    def to_openai_format(self):
        out = []
        if self.system_prompt:
            out.append({"role": "system", "content": self.system_prompt})
        for m in self.messages:
            if m.role != "system":
                out.append({"role": m.role, "content": m.content})
        return out

    def to_chat_text(self):
        lines = []
        if self.system_prompt:
            lines.append("System: " + self.system_prompt)
        for m in self.messages:
            lines.append(f"{m.role.capitalize()}: {m.content}")
        return "\n".join(lines)

    def clear(self):
        self.messages = []
