"""Pure functions for cleaning raw ingredient strings before taxonomy lookup. No I/O."""

import re

UNITS = {
    "cup",
    "cups",
    "c",
    "tbsp",
    "tbsps",
    "tablespoon",
    "tablespoons",
    "tsp",
    "tsps",
    "teaspoon",
    "teaspoons",
    "oz",
    "ounce",
    "ounces",
    "lb",
    "lbs",
    "pound",
    "pounds",
    "g",
    "gram",
    "grams",
    "kg",
    "ml",
    "l",
    "liter",
    "liters",
    "litre",
    "pinch",
    "dash",
    "can",
    "cans",
    "jar",
    "package",
    "packages",
    "pkg",
    "bunch",
    "handful",
    "slice",
    "slices",
    "piece",
    "pieces",
    "stick",
    "sticks",
    "sprig",
    "sprigs",
    "head",
    "heads",
    "quart",
    "pint",
}

PREP_WORDS = {
    "diced",
    "chopped",
    "minced",
    "sliced",
    "grated",
    "shredded",
    "crushed",
    "peeled",
    "seeded",
    "cubed",
    "julienned",
    "halved",
    "quartered",
    "finely",
    "roughly",
    "coarsely",
    "thinly",
    "freshly",
    "packed",
    "softened",
    "melted",
    "divided",
    "trimmed",
    "rinsed",
    "drained",
    "beaten",
    "cooked",
    "uncooked",
    "toasted",
    "to",
    "taste",
    "for",
    "garnish",
    "serving",
    "optional",
    "plus",
    "more",
    "about",
    "or",
    "and",
    "of",
    "a",
    "an",
}

# leading words that can be dropped without changing the food; an allowlist so "coconut milk" never becomes "milk"
MODIFIERS = {
    "large",
    "small",
    "medium",
    "extra-large",
    "jumbo",
    "organic",
    "baby",
    "ripe",
    "raw",
    "whole",
    "boneless",
    "skinless",
    "lean",
    "yellow",
    "white",
    "red",
    "green",
    "orange",
    "purple",
    "unsalted",
    "salted",
    "plain",
    "low-sodium",
    "reduced-sodium",
    "light",
    "frozen",
    "ground",
}

FRACTIONS = "½⅓⅔¼¾⅛⅜⅝⅞"
QUANTITY = re.compile(rf"^[\d{FRACTIONS}/.\-–]+$")


def clean(raw: str | None) -> str:
    """Lowercase; drop parentheses, text after a comma, leading quantities and units."""
    text = (raw or "").lower().strip()
    text = re.sub(r"\(.*?\)", " ", text)  # "(about 2 cups)"
    text = text.split(",")[0]  # "onion, diced" -> "onion"
    words = text.split()
    while words and QUANTITY.match(words[0]):  # leading only, so "red 40" keeps its number
        words = words[1:]
    words = [w for w in words if w not in UNITS]
    # "3 cloves garlic": clove is a unit only when another word follows
    if len(words) > 1 and words[0] in ("clove", "cloves"):
        words = words[1:]
    return " ".join(words)


def strip_prep(text: str) -> str:
    """Remove prep words ("diced", "to taste") from an already cleaned string."""
    return " ".join(w for w in text.split() if w not in PREP_WORDS)


def singular(word: str) -> str:
    """Naive English singular for the last word of an ingredient name."""
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("oes"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def candidates(text: str) -> list[tuple[str, str]]:
    """Lookup keys to try in order, each tagged with how it was derived."""
    words = text.split()
    if not words:
        return []
    out = [
        (text, "exact"),
        (" ".join(words[:-1] + [singular(words[-1])]), "singular"),
        (" ".join(words[:-1] + [words[-1] + "s"]), "plural"),
    ]
    while len(words) > 1 and words[0] in MODIFIERS:
        words = words[1:]
        out.append((" ".join(words), "modifier_stripped"))
        out.append((" ".join(words[:-1] + [singular(words[-1])]), "modifier_stripped"))
    return out
