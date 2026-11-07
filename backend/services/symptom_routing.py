from functools import lru_cache
from pathlib import Path

import yaml

from schemas.symptom_log import SymptomRoute

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_routing(data_dir: Path = DATA_DIR) -> dict:
    """Read symptom_routing.yaml: safety_messages, ordered rules and the default route."""
    return yaml.safe_load((data_dir / "symptom_routing.yaml").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def get_routing() -> dict:
    return load_routing()


def _matches(rule: dict, sensation: str, location: str) -> bool:
    """A rule with no locations or no sensations matches any value for that field."""
    if "locations" in rule and location not in rule["locations"]:
        return False
    if "sensations" in rule and sensation not in rule["sensations"]:
        return False
    return True


def route_symptom(sensation: str, location: str, routing: dict | None = None) -> SymptomRoute:
    """Return the first matching rule's route, or the default."""
    routing = routing or get_routing()  # get routing from yaml
    sensation, location = sensation.strip().lower(), location.strip().lower()  # normalize
    rule = next(
        (r for r in routing["rules"] if _matches(r, sensation, location)), routing["default"]
    )  # if matches -> matched, else -> default (model, other)
    return SymptomRoute(
        route=rule["route"],
        family=rule.get("family"),
        safety_message=routing["safety_messages"].get(rule["route"]),
    )
