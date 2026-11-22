"""Generated symptoms must only use sensations and locations the app offers."""

import re
from pathlib import Path

from scripts.mock_users.shapes import load_user_types
from scripts.mock_users.symptoms import BACKGROUND_SYMPTOMS

# Beside backend/ locally, mounted at /frontend in Docker.
OPTIONS_PATHS = [
    Path(__file__).resolve().parents[2] / "frontend/src/types/symptomOptions.ts",
    Path("/frontend/src/types/symptomOptions.ts"),
]


def _options(source, name):
    match = re.search(rf"export const {name} = \[(.*?)\];", source, re.S)
    assert match, f"{name} not found in symptomOptions.ts"
    return set(re.findall(r"'([^']+)'", match.group(1)))


def test_generated_symptoms_use_app_options():
    path = next(p for p in OPTIONS_PATHS if p.is_file())
    source = path.read_text(encoding="utf-8")
    sensations, locations = _options(source, "sensationOptions"), _options(source, "locationOptions")
    types, _ = load_user_types()
    kinds = BACKGROUND_SYMPTOMS + [t.trigger.symptom for t in types.values() if t.trigger]

    for kind in kinds:
        assert kind.sensation in sensations, kind.sensation
        assert kind.location in locations, kind.location
