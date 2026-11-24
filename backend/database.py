"""Database connection and session management."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

Base = declarative_base()

# Tables whose models were removed. drop_all only knows the current models, and these still hold foreign keys to
# tables it drops (users, components), so a full reset must drop them first.
LEGACY_TABLES = ("user_component_states",)


def drop_all_tables(bind) -> None:
    """Drop every model table plus any legacy tables left over from removed models. Destructive."""
    with bind.begin() as conn:
        for table in LEGACY_TABLES:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
    Base.metadata.drop_all(bind=bind)


from auth_context import register_ownership_filter  # noqa: E402

register_ownership_filter()


def get_db():
    """
    Dependency function to get database session.

    Yields database session and ensures it's closed after use.
    Use in FastAPI routes with Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
