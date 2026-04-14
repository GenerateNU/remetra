# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All development commands use the `just` command runner (see `justfile`). Run `just --list` to see all available commands.

| Command | Purpose |
|---------|---------|
| `just setup` | Build Docker images (first-time setup) |
| `just dev` | Start development server with hot reload |
| `just rebuild` | Rebuild Docker images after adding dependencies |
| `just down` | Stop all Docker containers |
| `just test` | Run all backend tests with 90% coverage requirement |
| `just lint` | Run Ruff linter |
| `just format` | Auto-fix formatting with Ruff |
| `just shell` | Open shell inside backend container |
| `just logs` | View backend logs (all services) |
| `just logs-backend` | Tail backend logs only |
| `just logs-db` | Tail database logs only |
| `just seed` | Seed dev data (idempotent) |
| `just seed-clear` | Clear and re-seed dev data |
| `just seed-rag` | Ingest PDFs into RAG pipeline |
| `just reset-db` | Destructive schema reset (wipes all data) |
| `just clean` | Wipe Docker volumes |
| `just fe` | Start frontend Expo dev server |
| `just fe-ios` | Start frontend for iOS |
| `just fe-android` | Start frontend for Android |
| `just fe-install` | Install frontend npm dependencies |
| `just fe-test` | Run frontend tests |
| `just fe-test-coverage` | Run frontend tests with coverage |

**Run a single test:**
```bash
docker compose run --rm backend pytest tests/test_symptom_log.py
docker compose run --rm backend pytest -k test_create_symptom_log
```

**Frontend:**
```bash
cd frontend && npm test           # Run all tests
cd frontend && npm run test:watch  # Watch mode
cd frontend && npx expo start     # Start dev server
```

**Add Python dependencies:**
```bash
cd backend
uv add <package>        # Runtime dependency
uv add --dev <package>  # Dev dependency
```

Always commit both `pyproject.toml` and `uv.lock` after adding dependencies. Never use `pip install` directly.

## Architecture

Remetra is an autoimmune symptom tracking platform with an LLM/RAG pipeline for contextual food tagging. The backend runs in Docker; the frontend is a React Native/Expo mobile app.

### Backend (FastAPI + PostgreSQL + pgvector)

**N-Tier layered architecture — dependencies flow downward only:**
```
Router → Service → Repository → Database
```

- **Routers** (`backend/routers/`) — HTTP endpoints only, no business logic
- **Services** (`backend/services/`) — all business logic; 90% test coverage required
- **Repositories** (`backend/repositories/`) — all database access; 90% test coverage required
- **Models** (`backend/models/`) — SQLAlchemy ORM table definitions
- **Schemas** (`backend/schemas/`) — Pydantic v2 request/response validation

**Key patterns:**
- DB session (`db: Session`) is passed per method — never stored on the class
- Repositories use try/except with `db.rollback()` on write operations
- Services instantiate repositories inside `__init__` via `self.repo = SomeRepository()`
- Routers instantiate services inside each handler: `service = SomeService()`
- All models use UUID primary keys
- `FoodResponse` and `FoodLogResponse` use `model_config = ConfigDict(from_attributes=True)`

**Auth:**
- JWT bearer tokens via `OAuth2PasswordBearer`; `get_current_user()` dependency at `backend/routers/auth.py`
- `LoggingMiddleware` at `backend/middleware/logging_middleware.py` logs all requests/responses to `app.log`
- CORS is open (all origins) — configured in `backend/main.py`

### RAG Pipeline

**Files:** `backend/services/ingest.py`, `backend/services/ingest_service.py`, `backend/services/RAGTaggingService.py`, `backend/services/pdfconvert.py`, `backend/repositories/chunk_repository.py`

**Flow:**
1. PDFs in `backend/data/raw/` are parsed via `pypdf` (all pages), chunked, and embedded using `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim vectors)
2. Embeddings stored in PostgreSQL via `pgvector` in the `knowledge_chunks` table
3. At food suggestion time, user input is embedded and similarity search retrieves top-k relevant chunks
4. Retrieved chunks + food name/ingredients are passed to Gemini LLM (`google-genai`) which returns structured ingredient + trigger bucket suggestions
5. Suggestions are **never persisted** — returned in response only, user confirms before saving

**Seeding endpoints:**
- `POST /ingest/pdf` — upload a single PDF file
- `POST /ingest/folder` — seed all PDFs from `backend/data/raw/` (idempotent, clears by source before re-inserting)

**Suggestion endpoint:**
- `POST /food/suggestions` — accepts `FoodSuggestionRequest` (name, ingredients, optional selected_tag_ids), returns `SuggestedTagsAndIngredientsResponse`, no DB writes

**Important:** `ingest.py` contains pure functions only (parse, chunk, embed, similarity_search) — no DB calls. `ingest_service.py` handles orchestration and DB persistence.

### Tagging System

- Tags live on `Food` via the `FoodTag` join table — **not** on `FoodLog`
- `Tag` model has `is_system` (bool) — True for predefined trigger buckets, False for user-defined custom tags
- System tags are seeded at startup: gluten, FODMAPs, nightshades, histamines, added sugar, artificial additives, dairy, FDA Big 9 allergens
- Tag confirmation flow: RAG suggests tags → user confirms → `POST /food/{food_id}/tags` persists confirmed tags
- `add_tags_to_food` in service re-fetches full `Tag` objects after inserting join rows to return `list[TagResponse]`

### Frontend (React Native + Zustand)

```
Screen (View) → Zustand Store / Local State → API Service → Backend
```

- **Screens** (`frontend/src/screens/`) — UI rendering; local state via `useState`/`useCallback`
- **API** (`frontend/src/api/`) — Axios client and typed service classes (e.g. `foodService.createFood()`)
- **Store** (`frontend/src/store/`) — Zustand global state (auth tokens, user info); `useAuthStore` is persisted via AsyncStorage
- **Components** (`frontend/src/components/`) — reusable UI
- Bearer token interceptor wires the auth store to all API calls (`frontend/src/api/client.ts`)

### Testing

**Backend test fixtures** (`backend/conftest.py`):
- `db_session` — transactional isolation per test (rolls back after each test)
- `test_client` — FastAPI `TestClient` with `get_db` overridden to use `db_session`
- `authenticated_user` — creates a real user + JWT token; use this for auth-protected endpoints
- `sample_food_data`, `sample_symptom_data` — standard test data builders
- Bcrypt rounds are reduced to 4 in tests (vs 12 in prod) for speed

Coverage is measured only on `services/`, `repositories/`, and `main.py` (routers excluded). Threshold is 90%.

### Infrastructure

- `docker-compose.yml` — orchestrates backend, `test-db` (pgvector/pgvector:pg15), and pgAdmin
- pgAdmin UI: `http://localhost:5050` (one-time server setup: host=`test-db`, port=`5432`, user=`test_user`, pass=`test_password`, db=`test_remetra`)
- Backend API: `http://localhost:8000`, docs at `/scalar`
- Vector extension enabled automatically on startup via `CREATE EXTENSION IF NOT EXISTS vector`
- Tables created automatically on startup via `Base.metadata.create_all`
- Startup also runs a schema drift check — warns in logs if expected columns are missing
- Environment variables: copy `.env.example` to `.env`. Docker overrides `DATABASE_URL` to point at local `test-db`

## Code Conventions

- **Git commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, etc.)
- **Linting:** Ruff enforced via pre-commit hooks — run `just format` before committing
- **Test coverage:** Services and repositories must maintain 90% coverage (`just test` enforces this)
- **Tests:** Use Arrange → Act → Assert; test error cases with `pytest.raises()`; async tests use `asyncio_mode = auto`
- **Routing:** Always declare specific routes before dynamic `/{id}` routes in FastAPI routers
- **Schemas:** Use `ConfigDict(from_attributes=True)` on all response schemas; use `model_validate()` not `from_orm()`
- **Dependencies:** Always `uv add`, never `pip install`. Commit both `pyproject.toml` and `uv.lock`
- **Naming:** snake_case for files and functions, PascalCase for classes. Service files: `food_service.py`. Exception: `RAGTaggingService.py` (legacy, do not rename)
