#!/bin/sh
# Container entrypoint (local Docker and Railway): prepare the database, then start the API.
# Runs once per container start; uvicorn --reload restarts only the worker, not this script.
# Extra arguments are passed through to uvicorn (e.g. --reload locally).
set -e

python scripts/init_db.py
python scripts/seed_taxonomy.py

exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
