"""Seed script for loading mock data from data_generator into the database.

Usage inside Docker:
    python scripts/seed.py           # idempotent — skips existing records
    python scripts/seed.py --clear   # wipe seed data, then reseed
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Ensure /app (backend root) is importable when run as scripts/seed.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import delete, select, text

import models.food  # noqa: F401
import models.food_log  # noqa: F401
import models.knowledge_chunk  # noqa: F401
import models.metrics  # noqa: F401
import models.symptom  # noqa: F401
import models.symptom_log  # noqa: F401
import models.tag  # noqa: F401
import models.user  # noqa: F401
from database import Base, SessionLocal, engine
from models.food import Food
from models.food_log import FoodLog
from models.metrics import Metrics
from models.symptom import Symptom
from models.symptom_log import SymptomLog
from models.tag import FoodTag, Tag
from models.user import User
from services.auth_service import get_password_hash

SEED_DATA_DIR = Path("/seed_data")
SEED_USERS = [f"user_{i:03d}" for i in range(1, 41)]
SEED_PASSWORD = "testpassword"
SEED_TAG_NAMES = ["gluten", "dairy", "legumes", "shellfish", "soy", "fish", "egg", "peanuts"]


def _load_json(filename: str):
    with open(SEED_DATA_DIR / filename) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Seeding helpers
# ---------------------------------------------------------------------------


def seed_tags(db) -> dict[str, Tag]:
    """Upsert seed tags; return name → Tag map."""
    tag_map: dict[str, Tag] = {}
    created = 0
    for name in SEED_TAG_NAMES:
        tag = db.execute(select(Tag).where(Tag.name == name)).scalar_one_or_none()
        if not tag:
            tag = Tag(name=name, is_system=False)
            db.add(tag)
            db.flush()
            created += 1
        tag_map[name] = tag
    db.commit()
    print(f"  Tags: created {created}, skipped {len(SEED_TAG_NAMES) - created}")
    return tag_map


def seed_users(db) -> int:
    """Create 40 test users; skip if username already exists."""
    password_hash = get_password_hash(SEED_PASSWORD)
    created = 0
    for username in SEED_USERS:
        exists = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if not exists:
            db.add(
                User(
                    username=username,
                    email=f"{username}@seed.remetra.test",
                    password_hash=password_hash,
                )
            )
            created += 1
    db.commit()
    print(f"  Users: created {created}, skipped {len(SEED_USERS) - created}")
    return created


def seed_foods(db, tag_map: dict[str, Tag]) -> tuple[dict[str, Food], int]:
    """Create foods from foods.json + FoodTag rows; return name → Food map."""
    data = _load_json("foods.json")
    food_map: dict[str, Food] = {}
    created = 0
    for entry in data["foods"]:
        name = entry["food_name"]
        food = db.execute(select(Food).where(Food.name == name, Food.username.is_(None))).scalar_one_or_none()
        if food:
            food_map[name] = food
            continue
        food = Food(name=name, ingredients=entry["ingredients"], username=None)
        db.add(food)
        db.flush()
        for tag_name in entry.get("tags", []):
            tag = tag_map.get(tag_name)
            if tag:
                db.add(FoodTag(food_id=food.id, tag_id=tag.id))
        food_map[name] = food
        created += 1
    db.commit()
    skipped = len(data["foods"]) - created
    print(f"  Foods: created {created}, skipped {skipped}")
    return food_map, created


def seed_symptoms(db) -> tuple[dict[tuple[str, str], Symptom], int]:
    """Create one Symptom per unique (user_id, symptom_name); return lookup map."""
    data = _load_json("symptom_log.json")
    pairs: set[tuple[str, str]] = {(e["user_id"], e["symptom"]) for e in data}
    symptom_map: dict[tuple[str, str], Symptom] = {}
    created = 0
    for username, symptom_name in pairs:
        symptom = db.execute(
            select(Symptom).where(
                Symptom.username == username,
                Symptom.name == symptom_name,
            )
        ).scalar_one_or_none()
        if not symptom:
            symptom = Symptom(username=username, name=symptom_name)
            db.add(symptom)
            db.flush()
            created += 1
        symptom_map[(username, symptom_name)] = symptom
    db.commit()
    skipped = len(pairs) - created
    print(f"  Symptoms: created {created}, skipped {skipped}")
    return symptom_map, created


def seed_food_logs(db, food_map: dict[str, Food]) -> int:
    """Create FoodLog rows from food_logs.json; skip users who already have logs."""
    data = _load_json("food_logs.json")
    by_user: dict[str, list] = {}
    for entry in data:
        by_user.setdefault(entry["user_id"], []).append(entry)

    created_total = 0
    skipped_users = 0
    for username, entries in by_user.items():
        already_has_logs = db.execute(
            select(FoodLog.id).where(FoodLog.username == username).limit(1)
        ).scalar_one_or_none()
        if already_has_logs:
            skipped_users += 1
            continue
        logs = [
            FoodLog(
                username=username,
                food_id=food_map[entry["food_name"]].id,
                timestamp=datetime.fromisoformat(entry["timestamp"]),
            )
            for entry in entries
            if entry["food_name"] in food_map
        ]
        db.add_all(logs)
        created_total += len(logs)
    db.commit()
    print(f"  FoodLogs: created {created_total} (skipped {skipped_users} users already seeded)")
    return created_total


def seed_symptom_logs(db, symptom_map: dict[tuple[str, str], Symptom]) -> int:
    """Create SymptomLog rows from symptom_log.json; skip users who already have logs."""
    data = _load_json("symptom_log.json")
    by_user: dict[str, list] = {}
    for entry in data:
        by_user.setdefault(entry["user_id"], []).append(entry)

    created_total = 0
    skipped_users = 0
    for username, entries in by_user.items():
        already_has_logs = db.execute(
            select(SymptomLog.id).where(SymptomLog.username == username).limit(1)
        ).scalar_one_or_none()
        if already_has_logs:
            skipped_users += 1
            continue
        logs = [
            SymptomLog(
                username=username,
                symptom_id=symptom_map[(username, entry["symptom"])].id,
                intensity=entry["severity"],
                timestamp=datetime.fromisoformat(entry["timestamp"]),
            )
            for entry in entries
            if (username, entry["symptom"]) in symptom_map
        ]
        db.add_all(logs)
        created_total += len(logs)
    db.commit()
    print(f"  SymptomLogs: created {created_total} (skipped {skipped_users} users already seeded)")
    return created_total


# ---------------------------------------------------------------------------
# Clear helper
# ---------------------------------------------------------------------------


def clear_seed_data(db) -> None:
    """Delete seed data in reverse FK order, then commit."""
    print("Clearing seed data...")
    # Metrics reference symptoms — delete metrics for seed users first
    db.execute(delete(Metrics).where(Metrics.username.in_(SEED_USERS)))
    # Users cascade → food_logs, symptom_logs, symptoms
    db.execute(delete(User).where(User.username.in_(SEED_USERS)))
    # Seed foods (shared, username IS NULL) cascade → food_tags + food_logs
    seed_food_names = [e["food_name"] for e in _load_json("foods.json")["foods"]]
    db.execute(delete(Food).where(Food.name.in_(seed_food_names), Food.username.is_(None)))
    db.commit()
    print("Cleared.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Remetra with mock data.")
    parser.add_argument("--clear", action="store_true", help="Clear seed data before reseeding.")
    args = parser.parse_args()

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.clear:
            clear_seed_data(db)

        print("Seeding tags...")
        tag_map = seed_tags(db)

        print("Seeding users...")
        seed_users(db)

        print("Seeding foods...")
        food_map, _ = seed_foods(db, tag_map)

        print("Seeding symptoms...")
        symptom_map, _ = seed_symptoms(db)

        print("Seeding food logs...")
        seed_food_logs(db, food_map)

        print("Seeding symptom logs...")
        seed_symptom_logs(db, symptom_map)

        print("\nDone.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
