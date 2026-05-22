from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.memory.conversation_memory import ConversationMemory


@dataclass
class AssistantResponse:
    text: str
    blocked: bool = False
    block_reason: str = ""
    latency_ms: float = 0.0
    model_id: str = ""


SYSTEM_PROMPT = (
    "You are a helpful personal assistant. Be concise. "
    "Don't help with illegal or harmful stuff. "
    "If you're not sure about a fact, say so."
)


class BaseAssistant(ABC):
    name = "assistant"
    model_id = ""

    def __init__(self, max_turns=10):
        self.memory = ConversationMemory(max_turns=max_turns, system_prompt=SYSTEM_PROMPT)

    def reset(self):
        self.memory.clear()

    @abstractmethod
    def chat(self, user_message: str) -> AssistantResponse:
        pass
