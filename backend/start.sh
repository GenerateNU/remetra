#!/bin/sh
# Railway / production startup script.
# Runs before uvicorn so tables exist when the dev user is seeded.
set -e

echo "==> Initializing database schema..."
uv run python scripts/init_db.py

echo "==> Seeding dev user..."
uv run python scripts/seed_dev_user.py

echo "==> Starting server..."
exec uv run uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
