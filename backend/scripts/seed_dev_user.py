"""Seed a persistent profile row for development data.

Usage:
    python scripts/seed_dev_user.py           # create dev user (idempotent)
    python scripts/seed_dev_user.py --clear   # delete the dev user and re-create

   Credentials exist on Clerk, first authenticated request for a Clerk user creates its own profile row.

    DEV_USER_USERNAME   (default: devuser)
    DEV_USER_EMAIL      (default: dev@remetra.test)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from sqlalchemy import delete, select

from database import SessionLocal
from models.user import User

load_dotenv()

DEV_USERNAME = os.getenv("DEV_USER_USERNAME", "devuser")
DEV_EMAIL = os.getenv("DEV_USER_EMAIL", "dev@remetra.test")


def seed_dev_user(db) -> None:
    existing = db.execute(select(User).where(User.username == DEV_USERNAME)).scalar_one_or_none()
    if existing:
        print(f"  Dev user '{DEV_USERNAME}' already exists — skipping.")
        return

    db.add(
        User(
            username=DEV_USERNAME,
            email=DEV_EMAIL,
        )
    )
    db.commit()
    print(f"  Dev user '{DEV_USERNAME}' created (email: {DEV_EMAIL}).")


def clear_dev_user(db) -> None:
    db.execute(delete(User).where(User.username == DEV_USERNAME))
    db.commit()
    print(f"  Dev user '{DEV_USERNAME}' deleted.")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Seed dev user for Remetra.")
    parser.add_argument("--clear", action="store_true", help="Delete and re-create the dev user.")
    args = parser.parse_args()

    if SessionLocal is None:
        print("ERROR: DATABASE_URL is not set. Check your .env file.")
        sys.exit(1)

    db = SessionLocal()
    try:
        if args.clear:
            clear_dev_user(db)
        seed_dev_user(db)
    finally:
        db.close()

    print("Done.")


if __name__ == "__main__":
    main()
