"""Validate the taxonomy files in backend/data/taxonomy/.

Run from backend/: python -m scripts.validate_taxonomy   (exit code 1 on any error)
Also runs in CI through tests/test_taxonomy_data.py.
"""

import csv
import sys
from pathlib import Path

import yaml

from services.taxonomy_service import DATA_DIR, UNKNOWN, TaxonomyService, load_taxonomy

CONF = {"high", "medium", "low"}
CATEGORIES = {"fodmap", "protein_allergen", "food_chemical", "meal_property"}
ING_COLS = [
    "id",
    "canonical_name",
    "aliases",
    "groups",
    "std_serving_g",
    "components",
    "fat_g_per_100g",
    "fiber_g_per_100g",
    "elimination_base",
    "mapping_confidence",
    "notes",
]
PAIR_COLS = [
    "ingredient_id",
    "canonical_name",
    "component",
    "level",
    "confidence",
    "rationale",
    "source",
    "level_basis",
    "notes",
]

# design doc worked examples: canonical name -> (std serving g, components)
WORKED = {
    "garlic": ("3", {"fructans_allium": 3}),
    "garlic-infused oil": ("14", {}),
    "onion": ("40", {"fructans_allium": 3}),
    "scallion green tops": ("10", {}),
    "wheat bread": ("60", {"gluten": 3, "fructans_grain": 2}),
    "seitan": ("85", {"gluten": 3, "fructans_grain": 1}),
    "milk": ("250", {"lactose": 3, "milk_protein": 3}),
    "lactose-free milk": ("250", {"milk_protein": 3}),
    "aged cheddar": ("30", {"milk_protein": 2, "biogenic_amines": 2}),
    "parmesan": ("15", {"milk_protein": 2, "biogenic_amines": 3}),
    "canned chickpeas": ("80", {"gos": 1}),
    "apple": ("150", {"excess_fructose": 3, "sorbitol": 3}),
    "button mushrooms": ("75", {"mannitol": 3}),
    "tomato": ("120", {"acidic": 2, "histamine_liberators": 2, "nightshades": 3}),
    "soy sauce": ("15", {"gluten": 2, "soy": 2, "biogenic_amines": 2}),
    "red wine": ("150", {"alcohol": 3, "biogenic_amines": 2, "sulfites": 2}),
    "coffee": ("240", {"caffeine": 3, "acidic": 1}),
    "shrimp": ("85", {"shellfish": 3, "sulfites": 1}),
    "bell pepper": ("75", {"nightshades": 3}),
    "jalapeño": ("15", {"nightshades": 2, "capsaicin": 2}),
    "honey": ("20", {"excess_fructose": 3}),
    "plum": ("130", {"sorbitol": 3}),
    "beef": ("120", {"mammalian_meat": 3}),
}
ELIMINATION_BASE = {
    "white rice",
    "quinoa",
    "chicken breast",
    "turkey breast",
    "carrots",
    "zucchini",
    "green beans",
    "cucumber",
    "lettuce",
    "olive oil",
    "garlic-infused oil",
    "salt",
    "fresh parsley",
    "fresh ginger",
    "maple syrup",
}
# open team decisions: reported as warnings until resolved, then remove from this set
KNOWN_PURITY_CONFLICTS = {"maple syrup", "zucchini", "green beans"}


def parse_components(s):
    out = {}
    for tok in filter(None, s.split(";")):
        c, lv = tok.split(":")
        out[c] = int(lv)
    return out


def run_checks(data_dir: Path = DATA_DIR) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    errors: list[str] = []
    warnings: list[str] = []
    err = errors.append
    warn = warnings.append
    comp_yaml = yaml.safe_load((data_dir / "components.yaml").read_text(encoding="utf-8"))
    comps = {c["id"]: c for c in comp_yaml["components"]}
    if len(comps) != len(comp_yaml["components"]):
        err("duplicate component ids in components.yaml")
    meal_level = {c for c, d in comps.items() if "meal_level" in (d.get("flags") or [])}
    for cid, c in comps.items():
        for key in (
            "display_name",
            "category",
            "definition",
            "inclusion_confidence",
            "inclusion_rationale",
            "family_profile",
            "prior_tier",
        ):
            if not c.get(key):
                err(f"component {cid}: missing {key}")
        if c.get("category") not in CATEGORIES:
            err(f"component {cid}: bad category {c.get('category')}")
        if c.get("inclusion_confidence") not in CONF or c.get("prior_tier") not in CONF:
            err(f"component {cid}: bad inclusion_confidence or prior_tier")
        for fam, v in (c.get("family_profile") or {}).items():
            if not 0.01 <= float(v) <= 1:
                err(f"component {cid}: phi {fam}={v} outside 0.01-1")
        if not c.get("sources"):
            warn(f"component {cid}: no source for inclusion rationale")
    for g in comp_yaml.get("merge_groups", []):
        for m in g["members"]:
            if m not in comps:
                err(f"merge group {g['id']}: unknown member {m}")

    with open(data_dir / "ingredients.csv", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != ING_COLS:
            err(f"ingredients.csv columns {rd.fieldnames} != {ING_COLS}")
        ings = list(rd)
    ids = [r["id"] for r in ings]
    names = [r["canonical_name"] for r in ings]
    for dup in {i for i in ids if ids.count(i) > 1}:
        err(f"duplicate ingredient id {dup}")
    for dup in {n for n in names if names.count(n) > 1}:
        err(f"duplicate canonical_name {dup}")
    by_name = {r["canonical_name"]: r for r in ings}
    for r in ings:
        try:
            cm = parse_components(r["components"])
        except ValueError:
            err(f"{r['id']}: unparseable components '{r['components']}'")
            continue
        for c, lv in cm.items():
            if c not in comps:
                err(f"{r['id']}: unknown component {c}")
            if c in meal_level:
                err(f"{r['id']}: {c} is meal-level and must not be mapped from ingredients")
            if not 1 <= lv <= 3:
                err(f"{r['id']}: level {lv} for {c} outside 1-3 (omit zeros from this column)")
        if r["std_serving_g"]:
            try:
                float(r["std_serving_g"])
            except ValueError:
                err(f"{r['id']}: std_serving_g not numeric")
        if r["elimination_base"] not in ("true", "false"):
            err(f"{r['id']}: elimination_base must be true/false")
        if r["mapping_confidence"] not in CONF:
            err(f"{r['id']}: bad mapping_confidence")
    if not any(r["groups"] for r in ings):
        warn("groups column is empty for every ingredient; group validation rules skipped")

    with open(data_dir / "ingredient_components.csv", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != PAIR_COLS:
            err(f"ingredient_components.csv columns {rd.fieldnames} != {PAIR_COLS}")
        pairs = list(rd)
    seen = set()
    active = {}
    for p in pairs:
        key = (p["ingredient_id"], p["component"])
        if p["ingredient_id"] not in set(ids):
            err(f"pair {key}: ingredient not in ingredients.csv")
        if p["component"] not in comps:
            err(f"pair {key}: unknown component")
        if not p["level"].isdigit() or not 0 <= int(p["level"]) <= 3:
            err(f"pair {key}: level '{p['level']}' not 0-3")
        dropped = p["confidence"] == "n/a"
        if dropped and not p["rationale"].startswith("Dropped"):
            err(f"pair {key}: confidence n/a is only allowed on dropped rows")
        if not dropped and p["confidence"] not in CONF:
            err(f"pair {key}: bad confidence {p['confidence']}")
        if not p["rationale"]:
            err(f"pair {key}: missing rationale")
        if key in seen:
            err(f"duplicate pair {key}")
        seen.add(key)
        if not dropped and int(p["level"]) > 0:
            active.setdefault(p["ingredient_id"], {})[p["component"]] = int(p["level"])
    for r in ings:
        if parse_components(r["components"]) != active.get(r["id"], {}):
            err(f"{r['id']}: components column does not match ingredient_components.csv")

    for name, (serv, want) in WORKED.items():
        r = by_name.get(name)
        if r is None:
            err(f"worked example missing: {name}")
            continue
        if parse_components(r["components"]) != want or r["std_serving_g"] != serv:
            err(f"worked example mismatch: {name} has {r['components']} @ {r['std_serving_g']} g")

    flagged = {r["canonical_name"] for r in ings if r["elimination_base"] == "true"}
    for missing in ELIMINATION_BASE - flagged:
        err(f"elimination base ingredient missing or not flagged: {missing}")
    for name in flagged:
        if by_name[name]["components"]:
            msg = f"elimination base not pure: {name} has {by_name[name]['components']}"
            (warn if name in KNOWN_PURITY_CONFLICTS else err)(msg)

    try:
        tax = TaxonomyService(load_taxonomy(data_dir))
    except ValueError as e:  # alias collision
        err(str(e))
        return errors, warnings
    m = tax.lookup("definitely not a food 123")
    if m.ingredient_id != UNKNOWN or m.components:
        err("unknown fallback did not return 'unknown'")
    for bad in ("", None, "   "):
        try:
            tax.lookup(bad)
        except Exception as e:  # noqa: BLE001 - any exception here is a failure
            err(f"lookup({bad!r}) raised {e!r}")

    return errors, warnings


def main() -> int:
    errors, warnings = run_checks()
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"\n{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
