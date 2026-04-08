"""
Remetra API - Main application entry point.

This module initializes the FastAPI application and registers all route handlers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import text

from database import Base, engine
from middleware.logging_middleware import LoggingMiddleware
from routers.algorithm_router import router as algorithm_router
from routers.auth import router as auth_router
from routers.food_log_router import router as food_log_router
from routers.food_router import router as food_router
from routers.ingest_router import router as ingest_router
from routers.symptom_log_router import router as symptom_log_router
from routers.symptom_router import router as symptom_router
from routers.tag_router import router as tag_router


def _sync_schema() -> None:
    """Add any columns present in SQLAlchemy models but missing from the live DB.

    create_all only creates brand-new tables; this handles new columns on
    existing tables so deploys never break due to schema drift.
    """
    inspector = sa_inspect(engine)
    with engine.connect() as conn:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue  # create_all will handle brand-new tables
            existing = {col["name"] for col in inspector.get_columns(table.name)}
            for col in table.columns:
                if col.name not in existing:
                    col_type = col.type.compile(engine.dialect)
                    conn.execute(text(f"ALTER TABLE {table.name} ADD COLUMN IF NOT EXISTS {col.name} {col_type}"))
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine is not None:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        Base.metadata.create_all(bind=engine)
        _sync_schema()
    yield


app = FastAPI(
    title="Remetra API",
    description="Backend API for Remetra 😛",
    version="0.1.0",
    lifespan=lifespan,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Replace the auto-generated OAuth2PasswordBearer scheme with a simple
    # HTTPBearer scheme so the Scalar/Swagger "Authorize" button accepts a
    # raw token instead of attempting an OAuth2 form-based password flow.
    schema.setdefault("components", {})["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Rewrite per-route security references so Scalar attaches the token.
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            if isinstance(operation, dict) and "security" in operation:
                operation["security"] = [{"BearerAuth": []}]
    schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(LoggingMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(algorithm_router)
app.include_router(symptom_log_router)
app.include_router(symptom_router)
app.include_router(food_router)
app.include_router(ingest_router)
app.include_router(food_log_router)
app.include_router(tag_router)


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    """
    Scalar API documentation endpoint.

    Access at /scalar for interactive API docs.

    Returns:
        HTMLResponse: Scalar documentation page
    """
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )


@app.get("/", tags=["Health"])
async def root() -> dict[str, str]:
    """
    Root endpoint

    Returns:
        dict: API name and status message
    """
    return {"message": "Remetra API", "status": "running"}


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint

    Returns:
        dict: Service health status
    """
    return {"status": "healthy"}
