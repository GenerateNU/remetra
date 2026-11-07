"""Seed initial user_component_states from onboarding conditions.

Usage inside Docker:
    python scripts/seed_onboarding.py                  # all users without state
    python scripts/seed_onboarding.py --user alice123   # one specific user
"""

import argparse
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import Base, SessionLocal, engine
from models.user import User
from services.onboarding_service import OnboardingService


def main():
    parser = argparse.ArgumentParser(description="Seed onboarding state for users.")
    parser.add_argument("--user", type=str, help="Seed a specific user by username.")
    args = parser.parse_args()

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    service = OnboardingService()
    try:
        if args.user:
            count = service.initialize_user_state(db, args.user)
            print(f"  {args.user}: created {count} rows.")
        else:
            users = db.query(User).all()
            total = 0
            skipped = 0
            for user in users:
                count = service.initialize_user_state(db, user.username)
                if count:
                    total += count
                else:
                    skipped += 1
            print(f"  Seeded {total} rows across {len(users) - skipped} users, skipped {skipped} already seeded.")

        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
