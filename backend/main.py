"""
Remetra API - Main application entry point.

This module initializes the FastAPI application and registers all route handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import text

from database import Base, engine
import models
from middleware.logging_middleware import LoggingMiddleware
from routers.food_router import router as food_router
from routers.symptom_log_route import router as symptom_log_router
from routers.food_log_router import router as food_log_router
from routers.auth import router as auth_router

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Remetra API",
    description="Backend API for Remetra 😛",
    version="0.1.0",
)

app.add_middleware(LoggingMiddleware)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
app.include_router(auth.router)
app.include_router(symptom_log_router)
=======
app.include_router(auth_router)
>>>>>>> 56bccbf (WIP: 2)
app.include_router(food_router)
app.include_router(food_log_router)


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
