"""Seed taxonomy data from CSV/YAML files into the database.

The taxonomy is read-only reference data that ships with the code, so each run replaces the
three tables' contents in a single transaction. Re-running never duplicates rows, edited
values are updated, and rows removed from the files are removed from the database. If any
row is invalid (e.g. a mapping references an unknown slug) the whole run rolls back.

Expects the schema to exist already (run scripts/init_db.py first).

Usage inside Docker:
    python scripts/seed_taxonomy.py              # replace taxonomy rows
    python scripts/seed_taxonomy.py --recreate   # drop + recreate the 3 taxonomy tables first
                                                 # (local use, after changing their models)
"""

import argparse
import csv
import sys
from pathlib import Path

import yaml
from sqlalchemy import delete, insert, select, text

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Base, SessionLocal, engine
from models.component import Component
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent

TAXONOMY_DIR = Path(__file__).resolve().parent.parent / "data" / "taxonomy"
INGREDIENTS_CSV = TAXONOMY_DIR / "ingredients.csv"
COMPONENTS_YAML = TAXONOMY_DIR / "components.yaml"
INGREDIENT_COMPONENTS_CSV = TAXONOMY_DIR / "ingredient_components.csv"


def _read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _split(value: str) -> list[str]:
    """Parse a semicolon-separated CSV cell into a list ("" -> [])."""
    return [part.strip() for part in value.split(";") if part.strip()]


def _optional(value: str, cast=str):
    return cast(value) if value else None


def ingredient_row(row: dict) -> dict:
    return {
        "slug": row["id"],
        "canonical_name": row["canonical_name"],
        "aliases": _split(row["aliases"]),
        "std_serving_g": _optional(row["std_serving_g"], int),
        "fat_g_per_100g": _optional(row["fat_g_per_100g"], float),
        "fiber_g_per_100g": _optional(row["fiber_g_per_100g"], float),
        "elimination_base": row["elimination_base"].strip().lower() == "true",
        "mapping_confidence": _optional(row["mapping_confidence"]),
        "notes": _optional(row["notes"]),
    }


def component_row(entry: dict) -> dict:
    return {
        "slug": entry["id"],
        "display_name": entry["display_name"],
        "category": entry["category"],
        "definition": entry.get("definition"),
        "inclusion_confidence": entry["inclusion_confidence"],
        "inclusion_rationale": entry.get("inclusion_rationale"),
        "sources": entry.get("sources") or [],
        "prior_tier": entry["prior_tier"],
        "flags": entry.get("flags") or [],
    }


def mapping_row(row: dict, ingredient_ids: dict, component_ids: dict) -> dict:
    try:
        ingredient_id = ingredient_ids[row["ingredient_id"]]
        component_id = component_ids[row["component"]]
    except KeyError as missing:
        raise ValueError(f"ingredient_components.csv references unknown slug {missing} in row {row}") from None
    return {
        "ingredient_id": ingredient_id,
        "component_id": component_id,
        "concentration_level": int(row["concentration_level"]),
        "confidence": row["confidence"],
        "rationale": _optional(row["rationale"]),
        "source": _optional(row["source"]),
        "concentration_basis": _optional(row["concentration_basis"]),
        "notes": _optional(row["notes"]),
    }


def seed(db) -> dict[str, int]:
    """Replace all taxonomy rows. Caller owns the transaction."""
    # Serialize concurrent seeders (e.g. several replicas starting at once); released at commit.
    db.execute(text("SELECT pg_advisory_xact_lock(hashtext('seed_taxonomy'))"))
    ingredients = [ingredient_row(r) for r in _read_csv(INGREDIENTS_CSV)]
    components = [component_row(c) for c in yaml.safe_load(COMPONENTS_YAML.read_text())["components"]]
    mapping_csv = _read_csv(INGREDIENT_COMPONENTS_CSV)

    db.execute(delete(IngredientComponent))
    db.execute(delete(Ingredient))
    db.execute(delete(Component))
    db.execute(insert(Ingredient), ingredients)
    db.execute(insert(Component), components)

    ingredient_ids = dict(db.execute(select(Ingredient.slug, Ingredient.id)).all())
    component_ids = dict(db.execute(select(Component.slug, Component.id)).all())
    mappings = [mapping_row(r, ingredient_ids, component_ids) for r in mapping_csv]
    db.execute(insert(IngredientComponent), mappings)

    return {"ingredients": len(ingredients), "components": len(components), "mappings": len(mappings)}


TAXONOMY_TABLES = [IngredientComponent.__table__, Ingredient.__table__, Component.__table__]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--recreate", action="store_true", help="drop and recreate the taxonomy tables first")
    args = parser.parse_args()

    if args.recreate:
        print("Recreating taxonomy tables...")
        Base.metadata.drop_all(bind=engine, tables=TAXONOMY_TABLES)
        Base.metadata.create_all(bind=engine, tables=TAXONOMY_TABLES)

    print("Seeding taxonomy...")
    with SessionLocal.begin() as db:
        counts = seed(db)
    print(f"  Ingredients: {counts['ingredients']}, Components: {counts['components']}, Mappings: {counts['mappings']}")
    print("Done.")


if __name__ == "__main__":
    main()
