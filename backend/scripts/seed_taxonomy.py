"""Seed taxonomy data from CSV/YAML files into the database.

Usage inside Docker:
    python scripts/seed_taxonomy.py
"""

import csv
import sys
from pathlib import Path

import yaml
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Base, SessionLocal, engine
from models.component import Component
from models.ingredient import Ingredient
from models.ingredient_component import IngredientComponent

TAXONOMY_DIR = Path(__file__).resolve().parent.parent / "data" / "taxonomy"
INGREDIENTS_CSV = TAXONOMY_DIR / "ingredients.csv"
COMPONENTS_YAML = TAXONOMY_DIR / "components.yaml"
INGREDIENT_COMPONENTS_CSV = TAXONOMY_DIR / "ingredient_components.csv"


def seed_ingredients(db):
    with open(INGREDIENTS_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        values = {
            "slug": row["id"],
            "canonical_name": row["canonical_name"],
            "aliases": row["aliases"] or None,
            "groups": row["groups"] or None,
            "std_serving_g": int(row["std_serving_g"]) if row["std_serving_g"] else None,
            "fat_g_per_100g": float(row["fat_g_per_100g"]) if row["fat_g_per_100g"] else None,
            "fiber_g_per_100g": float(row["fiber_g_per_100g"]) if row["fiber_g_per_100g"] else None,
            "mapping_confidence": row["mapping_confidence"] or None,
            "notes": row["notes"] or None,
        }
        stmt = insert(Ingredient).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={k: v for k, v in values.items() if k != "slug"},
        )
        db.execute(stmt)

    db.commit()
    print(f"  Ingredients: upserted {len(rows)} rows.")


def seed_components(db):
    with open(COMPONENTS_YAML) as f:
        data = yaml.safe_load(f)

    components = data["components"]
    for entry in components:
        values = {
            "slug": entry["id"],
            "display_name": entry["display_name"],
            "category": entry["category"],
            "definition": entry.get("definition"),
            "inclusion_confidence": entry["inclusion_confidence"],
            "inclusion_rationale": entry.get("inclusion_rationale"),
            "sources": entry.get("sources", []),
            "prior_tier": entry["prior_tier"],
            "flags": entry.get("flags", []),
        }
        stmt = insert(Component).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["slug"],
            set_={k: v for k, v in values.items() if k != "slug"},
        )
        db.execute(stmt)

    db.commit()
    print(f"  Components: upserted {len(components)} rows.")


def seed_ingredient_components(db):
    ingredient_map = {row.slug: row.id for row in db.query(Ingredient).all()}
    component_map = {row.slug: row.id for row in db.query(Component).all()}

    with open(INGREDIENT_COMPONENTS_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    skipped = 0
    upserted = 0
    for row in rows:
        ingredient_id = ingredient_map.get(row["ingredient_id"])
        component_id = component_map.get(row["component"])
        if not ingredient_id or not component_id:
            skipped += 1
            continue

        values = {
            "ingredient_id": ingredient_id,
            "component_id": component_id,
            "concentration_level": int(row["concentration_level"]),
            "confidence": row.get("confidence") or None,
            "rationale": row.get("rationale") or None,
            "source": row.get("source") or None,
            "concentration_basis": row.get("concentration_basis") or None,
            "notes": row.get("notes") or None,
        }
        stmt = insert(IngredientComponent).values(**values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ingredient_id", "component_id"],
            set_={
                k: v
                for k, v in values.items()
                if k not in ("ingredient_id", "component_id")
            },
        )
        db.execute(stmt)
        upserted += 1

    db.commit()
    print(f"  IngredientComponents: upserted {upserted}, skipped {skipped}.")


def main():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("Seeding taxonomy...")
        seed_ingredients(db)
        seed_components(db)
        seed_ingredient_components(db)
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
