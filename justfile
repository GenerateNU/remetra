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

test:
    docker compose up -d test-db
    sleep 3
    docker compose run --rm backend pytest --cov=services --cov=repositories --cov=main --cov-report=term-missing --cov-fail-under=100
    docker compose stop test-db

lint:
    docker compose run --rm backend ruff check .

format:
    docker compose run --rm backend ruff check --fix .
    docker compose run --rm backend ruff format .

shell:
    docker compose exec backend bash

logs:
    docker compose logs -f

logs-backend:
    docker compose logs -f backend