"""
Remetra API - Main application entry point.

This module initializes the FastAPI application and registers all route handlers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

app = FastAPI(
    title="Remetra API",
    description="Backend API for Remetra 😛",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
