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

# Seed the database with mock data from data_generator/ (idempotent)
seed:
    docker compose run --rm backend python scripts/seed.py

# Wipe all seed data and reseed from scratch
seed-clear:
    docker compose run --rm backend python scripts/seed.py --clear

# Drop all tables and recreate schema from scratch (destructive — local use only)
reset-db:
    docker compose run --rm backend python scripts/init_db.py --reset

# Ingest all PDFs from backend/data/raw/ into the RAG knowledge base
seed-rag:
    curl -X POST http://localhost:8000/ingest/folder

# --- Taxonomy (ingredients / components / mappings) ---------------------------

psql := "docker compose exec -T test-db psql -U test_user -d test_remetra -P pager=off"

# Seed taxonomy tables from backend/data/taxonomy/ (replaces all rows; safe to re-run)
seed-taxonomy:
    docker compose run --rm backend sh -c "python scripts/init_db.py && python scripts/seed_taxonomy.py"

# Drop + recreate only the taxonomy tables, then seed (use after changing their models)
seed-taxonomy-recreate:
    docker compose run --rm backend python scripts/seed_taxonomy.py --recreate

# Row counts for the three taxonomy tables
taxonomy-counts:
    @{{psql}} -c "SELECT 'ingredients' AS table_name, count(*) FROM ingredients UNION ALL SELECT 'components', count(*) FROM components UNION ALL SELECT 'ingredient_components', count(*) FROM ingredient_components"

# List components (e.g. gluten, lactose)
taxonomy-components:
    @{{psql}} -c "SELECT slug, display_name, category, prior_tier, inclusion_confidence, flags FROM components ORDER BY category, slug"

# List ingredients; optional case-insensitive filter on slug/name/aliases, e.g. `just taxonomy-ingredients bread`
taxonomy-ingredients filter="":
    @{{psql}} -c "SELECT slug, canonical_name, aliases, std_serving_g, elimination_base AS elim, mapping_confidence AS conf FROM ingredients WHERE '{{filter}}' = '' OR slug ILIKE '%{{filter}}%' OR canonical_name ILIKE '%{{filter}}%' OR aliases::text ILIKE '%{{filter}}%' ORDER BY slug"

# Ingredient -> component mappings; optional ingredient filter, e.g. `just taxonomy-mappings wheat_bread`
taxonomy-mappings ingredient="":
    @{{psql}} -c "SELECT i.slug AS ingredient, c.slug AS component, ic.concentration_level AS level, ic.confidence, ic.concentration_basis AS basis FROM ingredient_components ic JOIN ingredients i ON i.id = ic.ingredient_id JOIN components c ON c.id = ic.component_id WHERE '{{ingredient}}' = '' OR i.slug ILIKE '%{{ingredient}}%' OR i.canonical_name ILIKE '%{{ingredient}}%' ORDER BY i.slug, c.slug"

# Which ingredients contain a component, strongest first, e.g. `just taxonomy-component gluten`
taxonomy-component component:
    @{{psql}} -c "SELECT i.slug AS ingredient, ic.concentration_level AS level, ic.confidence, left(ic.rationale, 80) AS rationale FROM ingredient_components ic JOIN ingredients i ON i.id = ic.ingredient_id JOIN components c ON c.id = ic.component_id WHERE c.slug = '{{component}}' ORDER BY ic.concentration_level DESC, i.slug"

# Interactive psql shell on the local database (\dt, \d ingredients, ...)
db-psql:
    docker compose exec test-db psql -U test_user -d test_remetra

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
