"""Initialize database schema against any PostgreSQL target (local or Supabase).

Usage:
    python scripts/init_db.py           # create tables only (safe, idempotent)
    python scripts/init_db.py --reset   # DROP all tables then recreate (destructive)

Set DATABASE_URL in .env or as an environment variable before running.
For Supabase, use the direct connection string (not the pooler) so that
DDL statements like CREATE EXTENSION execute without transaction issues.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

# Import all models so their metadata is registered on Base before create_all.
import models.food  # noqa: F401
import models.food_log  # noqa: F401
import models.knowledge_chunk  # noqa: F401
import models.metrics  # noqa: F401
import models.symptom  # noqa: F401
import models.symptom_log  # noqa: F401
import models.tag  # noqa: F401
import models.user  # noqa: F401
from database import Base, engine


def init_db(reset: bool = False) -> None:
    if engine is None:
        print("ERROR: DATABASE_URL is not set. Check your .env file.")
        sys.exit(1)

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    print("pgvector extension: OK")

    if reset:
        print("--reset flag detected: dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("Tables dropped.")

    Base.metadata.create_all(bind=engine)
    print("Tables created/verified.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize Remetra DB schema.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop all tables before recreating (destructive — use with care on production).",
    )
    args = parser.parse_args()

    if args.reset:
        confirm = input("WARNING: This will drop all tables and data. Type 'yes' to confirm: ")
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    init_db(reset=args.reset)
    print("Done.")


if __name__ == "__main__":
    main()
