set dotenv-load

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

default:
    @just --list


setup:
    @echo "Building Docker Images"
    docker compose build
    @echo "Setup complete"

dev:
    docker compose up

rebuild:
    docker compose build --no-cache

down:
    docker compose down

clean:
    docker compose down -v

# Create mock users, replacing existing mock_ users. Usage: just mock [count] [seed] [days]
mock count="20" seed="42" days="60":
    docker compose run --rm backend python -m scripts.mock_users.generate --count {{count}} --seed {{seed}} --days {{days}}

# Delete mock_ users and their rows, leaving every other user alone
mock-clear:
    docker compose run --rm backend python -m scripts.mock_users.clear

# Check that the last `just mock` run's planted triggers stand out from background symptoms
mock-check:
    docker compose run --rm backend python -m scripts.mock_users.check

# Drop all tables and recreate schema from scratch (destructive — local use only)
reset-db:
    docker compose run --rm backend python scripts/init_db.py --reset

# Ingest all PDFs from backend/data/raw/ into the RAG knowledge base
seed-rag:
    curl -X POST http://localhost:8000/ingest/folder

test:
    docker compose up -d test-db
    sleep 3
    docker compose run --rm backend pytest --cov=services --cov=repositories --cov=main --cov-report=term-missing --cov-fail-under=90
    docker compose stop test-db

lint:
    docker compose run --rm backend ruff check .
    cd frontend && npm run lint

format:
    docker compose run --rm backend ruff check --fix .
    docker compose run --rm backend ruff format .

shell:
    docker compose exec backend bash

logs:
    docker compose logs -f

logs-backend:
    docker compose logs -f backend

logs-db:
    docker compose logs -f test-db

# Frontend commands (run locally, not in Docker)
fe:
    cd frontend && npm start

fe-ios:
    cd frontend && npm run ios

fe-android:
    cd frontend && npm run android

fe-install:
    cd frontend && npm install

fe-test:
    cd frontend && npm test

fe-test-coverage:
    cd frontend && npm run test:coverage
