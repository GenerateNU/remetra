"""Generates mock users with one seeded random generator, saves them, and writes the truth file.

Usage (from backend/):
    python -m scripts.mock_users.generate --count 20 --seed 42
"""

import argparse
import json
import random
from dataclasses import asdict
from datetime import date
from pathlib import Path

from database import SessionLocal
from scripts.init_db import init_db
from scripts.mock_users.health import build_health_days
from scripts.mock_users.meals import DEFAULT_DAYS, DEFAULT_SKIP_RATE, build_meals, pick_regular_foods
from scripts.mock_users.save import save_users
from scripts.mock_users.shapes import USERNAME_PREFIX, MockUserData, UserType, load_user_types
from scripts.mock_users.symptoms import build_symptoms, trigger_meals

DEFAULT_TRUTH_PATH = Path(__file__).resolve().parent / "output" / "truth.json"


def generate_users(
    seed: int,
    count: int,
    end_date: date,
    days: int = DEFAULT_DAYS,
    skip_rate: float = DEFAULT_SKIP_RATE,
    user_types: dict[str, UserType] | None = None,
    background_rate: float | None = None,
) -> list[MockUserData]:
    """Build `count` users ending on `end_date`. The same arguments always give the same users."""
    if user_types is None or background_rate is None:
        loaded_types, loaded_rate = load_user_types()
        user_types = user_types or loaded_types
        background_rate = loaded_rate if background_rate is None else background_rate
    type_list = list(user_types.values())
    rng = random.Random(seed)
    users = []
    for i in range(count):
        user_type = type_list[i % len(type_list)]  # take turns so each type gets about the same number of users
        regular = pick_regular_foods(rng)
        foods = [food for slot_foods in regular.values() for food in slot_foods]
        meals, skipped = build_meals(rng, regular, end_date, days, skip_rate)
        symptoms = build_symptoms(rng, meals, foods, user_type.trigger, background_rate, end_date, days, skipped)
        health = build_health_days(rng, symptoms, end_date, days)
        users.append(
            MockUserData(
                username=f"{USERNAME_PREFIX}{i + 1:03d}",
                user_type=user_type,
                foods=foods,
                meals=meals,
                symptoms=symptoms,
                skipped_days=skipped,
                health_days=health,
            )
        )
    return users


def truth_records(users: list[MockUserData]) -> list[dict]:
    """Each user's type and planted trigger, plus how often they ate it, for checking the model later."""
    records = []
    for user in users:
        trigger = user.user_type.trigger
        records.append(
            {
                "username": user.username,
                "user_type": user.user_type.name,
                "trigger": asdict(trigger) if trigger else None,
                "trigger_meals": len(trigger_meals(user.meals, user.foods, trigger.component)) if trigger else 0,
                "planted_reactions": sum(s.planted for s in user.symptoms),
                "background_symptoms": sum(not s.planted for s in user.symptoms),
            }
        )
    return records


def write_truth_file(users: list[MockUserData], path: Path, seed: int, end_date: date, days: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    truth = {"seed": seed, "end_date": end_date.isoformat(), "days": days, "users": truth_records(users)}
    path.write_text(json.dumps(truth, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate mock users, save them, and write the truth file.")
    parser.add_argument("--count", type=int, default=20, help="number of mock users")
    parser.add_argument("--seed", type=int, default=42, help="same seed, same data")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="days of history, ending today")
    parser.add_argument("--truth", type=Path, default=DEFAULT_TRUTH_PATH, help="where to write the truth file")
    args = parser.parse_args(argv)

    init_db()
    end_date = date.today()
    users = generate_users(args.seed, args.count, end_date, args.days)
    db = SessionLocal()
    try:
        save_users(db, users)
    finally:
        db.close()
    write_truth_file(users, args.truth, args.seed, end_date, args.days)

    for record in truth_records(users):
        print(
            f"{record['username']}  {record['user_type']:<13} trigger meals {record['trigger_meals']:>3}  "
            f"reactions {record['planted_reactions']:>3}  background {record['background_symptoms']:>3}"
        )
    print(f"Wrote truth file for {len(users)} users to {args.truth}")


if __name__ == "__main__":
    main()
