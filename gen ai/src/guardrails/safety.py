import re
from dataclasses import dataclass


class SafetyAction:
    ALLOW = "allow"
    BLOCK_INPUT = "block_input"
    REFUSE_OUTPUT = "refuse_output"


@dataclass
class SafetyResult:
    action: str
    reason: str = ""
    sanitized_text: str = ""


# regex list — not perfect but good enough for the assignment
JAILBREAK_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"disregard\s+(your\s+)?(safety|guidelines|rules)",
    r"pretend\s+you\s+are\s+(dan|evil|unrestricted)",
    r"jailbreak",
    r"bypass\s+(content\s+)?filter",
    r"developer\s+mode",
]

HARM_PATTERNS = [
    r"how\s+to\s+(make|build)\s+(a\s+)?bomb",
    r"how\s+to\s+hack",
    r"generate\s+(malware|ransomware)",
    r"steal\s+credit\s+card",
]

BIAS_PATTERNS = [
    r"which\s+(race|gender|religion)\s+is\s+(smarter|better|worse)",
    r"are\s+\w+\s+people\s+(inferior|superior)",
]

REFUSAL_MSG = (
    "I can't help with that. Happy to answer something else though."
)


def _hit(text, patterns):
    t = text.lower()
    return any(re.search(p, t, re.I) for p in patterns)


def check_input(user_text):
    if _hit(user_text, JAILBREAK_PATTERNS):
        return SafetyResult(SafetyAction.BLOCK_INPUT, "jailbreak-y phrasing")
    if _hit(user_text, HARM_PATTERNS):
        return SafetyResult(SafetyAction.BLOCK_INPUT, "harmful request")
    return SafetyResult(SafetyAction.ALLOW, sanitized_text=user_text)


def check_output(reply, user_text):
    if _hit(user_text + "\n" + reply, HARM_PATTERNS):
        return SafetyResult(SafetyAction.REFUSE_OUTPUT, "bad output", REFUSAL_MSG)
    return SafetyResult(SafetyAction.ALLOW, sanitized_text=reply)


def bias_safe_response(user_text):
    if _hit(user_text, BIAS_PATTERNS):
        return (
            "I don't compare groups by race, gender, religion, etc. "
            "Happy to talk about fairness or bias in AI if you want."
        )
    return None
