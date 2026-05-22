class ChatMemory:
    def __init__(self, max_turns=10, system=""):
        self.max_turns = max_turns
        self.system = system
        self.turns = []

    def add(self, role, text):
        self.turns.append({"role": role, "text": text})
        if len(self.turns) > self.max_turns * 2:
            self.turns = self.turns[-(self.max_turns * 2):]

    def prompt_block(self):
        lines = []
        if self.system:
            lines.append("System: " + self.system)
        for t in self.turns:
            lines.append(f"{t['role'].capitalize()}: {t['text']}")
        lines.append("Assistant:")
        return "\n".join(lines)

    def clear(self):
        self.turns = []
