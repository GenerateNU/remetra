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
    docker compose exec backend pytest

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