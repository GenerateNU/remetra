"""
Deterministic safety checks for the chatbot.

Pure functions only: no DB access and no model calls. Anything here is
enforced in code, so it holds even if the model ignores its instructions.
"""

import re

EMERGENCY_REPLY = (
    "This sounds like it could be a medical emergency. Please call 911 or your local emergency number now, "
    "or go to the nearest emergency room. If you are thinking about harming yourself, call or text 988 "
    "to reach the Suicide & Crisis Lifeline."
)

REFUSED_REPLY = (
    "I can't say whether that food is a trigger for you. Your report only flags a food once your logs "
    "show enough evidence for it. Keep logging, and bring any concerns to your care team."
)

# Matched against normalized text: lowercase, apostrophes removed, everything else non-alphanumeric
# collapsed to single spaces. So "Can't  breathe!" is matched as "cant breathe".
# TODO: review this list with the team; it is a starting set, not a clinical triage tool.
_EMERGENCY_PATTERNS = [
    re.compile(p)
    for p in (
        r"\b(cant|cannot|can not|unable to|struggling to|hard to|trouble) breath(e|ing)?\b",
        r"\bthroat\b.{0,30}?\b(closing|closed|swelling|swollen|tightening)\b",
        r"\b(lips?|tongue|face) (is |are )?(swelling|swollen)\b",
        r"\banaphyla",
        r"\bepi ?pen\b",
        r"\bchest (pain|pressure|tightness)\b",
        r"\b(passed|passing|pass) out\b",
        r"\bfaint(ed|ing)\b",
        r"\bseizure",
        r"\boverdos",
        r"\b(vomiting|throwing up|coughing up) blood\b",
        r"\b(kill|hurt|harm) myself\b",
        r"\bsuicid",
        r"\bend my life\b",
        r"\bwant to die\b",
    )
]


def _normalize(text: str) -> str:
    text = text.lower().replace("'", "").replace("\u2019", "")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def is_emergency(text: str) -> bool:
    """True if the text contains wording that needs the fixed safety reply."""
    normalized = _normalize(text)
    return any(pattern.search(normalized) for pattern in _EMERGENCY_PATTERNS)


def check_triggers(claimed: list[str], allowed: list[str]) -> bool:
    """True if every food the model called a trigger is already in the user's report."""
    allowed_names = {name.strip().lower() for name in allowed}
    return all(name.strip().lower() in allowed_names for name in claimed)
