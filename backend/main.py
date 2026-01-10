"""
Remetra API - Main application entry point.

This module initializes the FastAPI application and registers all route handlers.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Remetra API",
    description="Backend API for autoimmune symptom tracking and correlation",
    version="0.1.0",
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