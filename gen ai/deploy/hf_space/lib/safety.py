import re

JAILBREAK = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"jailbreak", r"developer\s+mode", r"bypass\s+filter",
]
HARM = [
    r"how\s+to\s+(make|build)\s+(a\s+)?bomb",
    r"how\s+to\s+hack", r"ransomware", r"malware",
]
BIAS = [
    r"which\s+(race|gender|religion)\s+is\s+(smarter|better)",
]


def _hit(text, pats):
    t = text.lower()
    return any(re.search(p, t, re.I) for p in pats)


def check_input(text):
    if _hit(text, JAILBREAK):
        return True, "jailbreak pattern"
    if _hit(text, HARM):
        return True, "harmful request"
    return False, ""


def bias_reply(text):
    if _hit(text, BIAS):
        return (
            "I won't rank people by race, gender, or religion. "
            "I can discuss fairness in AI if that's helpful."
        )
    return None


def check_output(reply, user_text):
    if _hit(user_text + reply, HARM):
        return "I can't help with that request."
    return reply
