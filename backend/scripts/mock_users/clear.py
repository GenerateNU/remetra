"""Deletes mock_ users and their rows. Every other user is left alone.

Usage (from backend/):
    python -m scripts.mock_users.clear
"""

import sys

from database import SessionLocal
from scripts.mock_users.save import clear_mock_users


def main() -> None:
    if SessionLocal is None:
        print("ERROR: DATABASE_URL is not set. Check your .env file.")
        sys.exit(1)

    db = SessionLocal()
    try:
        removed = clear_mock_users(db)
    finally:
        db.close()
    print(f"Removed {removed} mock users")


if __name__ == "__main__":
    main()
