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
        r"\b(lips?|tongue|face|mouth) (is |are |has |have |got |just |started |keeps? )*(swell\w*|swollen|puff\w*)\b",
        r"\bswelling (in|of|on) (my |the )?(lips?|tongue|face|mouth|throat)\b",
        r"\banaphyla",
        r"\bepi ?pen\b",
        r"\b(severe|serious|bad|major) (allergic )?reaction\b",
        r"\b(having|having an|in) (an )?allergic reaction\b",
        r"\bchest (pain|pressure|tightness)\b",
        r"\b(pain|pressure|tightness) in (my |the )?chest\b",
        r"\b(passed|passing|pass) out\b",
        r"\bfaint(ed|ing)\b",
        r"\bseizure",
        r"\boverdos",
        r"\b(vomiting|throwing up|coughing up) blood\b",
        r"\b(kill|hurt|harm) myself\b",
        r"\bunaliv",
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


# Food and ingredient words the answer-text check always looks for, on top of the user's own foods.
# Covers the system trigger buckets and FDA Big 9 allergens, plus common hunches.
COMMON_FOOD_TERMS = (
    "gluten", "wheat", "rye", "barley", "dairy", "milk", "lactose", "cheese", "egg", "soy", "peanut",
    "tree nut", "nut", "shellfish", "shrimp", "fish", "sesame", "fodmap", "nightshade", "tomato", "potato",
    "pepper", "histamine", "sugar", "added sugar", "artificial additive", "onion", "garlic", "caffeine",
    "coffee", "alcohol", "wine", "corn", "chocolate", "spicy food",
)  # fmt: skip

# Wording that presents a food as the cause of symptoms. Matched on normalized text.
_CLAIM = re.compile(
    r"\b(trigger\w*|caus\w*|culprit|to blame|react\w* to|sensitiv\w*|intoleran\w*|allergic to|"
    r"avoid\w*|cut \w+( \w+)? out|cut out|eliminat\w*|stop eating|flare\w*)\b"
)

# Wording the prompt asks for when logs don't support a claim ("your logs don't show that yet").
# Splits a sentence into clauses so a hedge only excuses the clause it is in.
_CONTRAST = re.compile(r"\b(but|though|although|however|that said|still)\b")

_NO_CLAIM = re.compile(
    r"\b(dont|doesnt|do not|does not|didnt|did not) (yet )?show\b|\bnot (yet|enough)\b|\bno evidence\b|"
    r"\b(cant|cannot|can not) (say|tell)\b|\btoo (early|soon)\b|\bnot (flagged|in your report|one of your)\b"
)


def _mentions(text: str, term: str) -> bool:
    return re.search(rf"\b{re.escape(term)}(s|es)?\b", text) is not None


def find_unreported_claims(answer: str, allowed: list[str], vocabulary: list[str]) -> list[str]:
    """
    Food names the answer text presents as a trigger that aren't in the user's report.

    Backs up check_triggers, which trusts the model to list its own claims. A sentence counts as a claim
    if it uses causal wording ("trigger", "causing", "avoid", ...) without the prompt's "logs don't show
    that yet" wording, and names a known food. Errs toward refusing: a refused answer is safer than a
    wrong trigger.
    """
    allowed_norm = [_normalize(name) for name in allowed if name.strip()]
    terms = {_normalize(term) for term in (*COMMON_FOOD_TERMS, *vocabulary) if term and term.strip()}
    terms -= {""}
    found: list[str] = []

    for sentence in re.split(r"(?<=[.!?])\s+|\n+", answer):
        for clause in _CONTRAST.split(_normalize(sentence)):
            if not _CLAIM.search(clause) or _NO_CLAIM.search(clause):
                continue
            for term in sorted(terms):
                covered = any(_mentions(name, term) or _mentions(term, name) for name in allowed_norm)
                if _mentions(clause, term) and not covered and term not in found:
                    found.append(term)
    return found
