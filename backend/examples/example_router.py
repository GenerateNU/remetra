"""
Example router showing how to wire together models, services, and HTTP endpoints.

Routers define your API endpoints - the URLs that clients/(our frontend) can call.
They receive HTTP requests, validate data, call services to do work, and send responses back to our frontend

This example shows:
- Defining endpoints (GET, POST) with proper HTTP methods
- Using Pydantic models to validate requests and format responses
- Calling service methods to handle business logic
- Returning appropriate HTTP status codes (200, 201, 404, 400)
- Organizing endpoints with tags for the API docs
"""

from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status

from examples.example_pydantic_models import (
    ChocolateCreate,
    ChocolateResponse,
    ErrorResponse,
    OrderCreate,
    OrderResponse,
)
from examples.example_service_layer import ChocolateService

# Create a router - this groups related endpoints together
router = APIRouter(
    prefix="/chocolates",  # All routes start with /chocolates
    tags=["Chocolates"],  # Groups endpoints in API docs
)

# In a real app, you'd inject the service via dependency injection
# For this example, we'll create it directly
chocolate_service = ChocolateService()


@router.post(
    "/",
    response_model=ChocolateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid chocolate data"},
    },
)
async def create_chocolate(chocolate: ChocolateCreate) -> ChocolateResponse:
    """
    Create a new chocolate product 😛🍫

    FastAPI automatically:
    - Validates the request body matches ChocolateCreate model
    - Returns 422 if validation fails
    - Converts the response to ChocolateResponse format
    - Shows this in the API docs with proper schemas

    - All of this stuff makes debugging easier and just makes it easier to work with the codebase as it expands

    Args:
        chocolate: Chocolate data from request body (auto-validated by FastAPI)

    Returns:
        The created chocolate with ID and timestamps

    Raises:
        HTTPException: If chocolate name already exists or validation fails
    """
    try:
        # Convert Pydantic model to dict for service layer as our service expects a dict
        chocolate_dict = chocolate.model_dump()

        # Call service to do the actual work
        created = await chocolate_service.create_chocolate(chocolate_dict)

        # FastAPI auto-converts dict to ChocolateResponse
        return created

    except ValueError as e:
        # Business logic errors become 400 Bad Request
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/",
    response_model=List[ChocolateResponse],
    responses={
        200: {"description": "List of chocolates"},
    },
)
async def get_chocolates(
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    in_stock_only: bool = False,
) -> List[ChocolateResponse]:
    """
    Get all chocolates with optional filtering.

    Query parameters are extracted automatically by FastAPI from the URL.
    Example: GET /chocolates?min_price=3.00&in_stock_only=true

    Args:
        min_price: Minimum price filter (optional query param)
        max_price: Maximum price filter (optional query param)
        in_stock_only: Only show in-stock items (optional query param)

    Returns:
        List of chocolates matching the filters
    """
    chocolates = await chocolate_service.get_chocolates(
        min_price=min_price, max_price=max_price, in_stock_only=in_stock_only
    )
    return chocolates


@router.get(
    "/{chocolate_id}",
    response_model=ChocolateResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Chocolate not found"},
    },
)
async def get_chocolate(chocolate_id: int) -> ChocolateResponse:
    """
    Get a specific chocolate by ID.

    Path parameters (like {chocolate_id}) are extracted from the URL automatically.
    Example: GET /chocolates/42 → chocolate_id = 42

    Args:
        chocolate_id: ID from URL path parameter

    Returns:
        The requested chocolate

    Raises:
        HTTPException: If chocolate ID doesn't exist
    """
    chocolate = await chocolate_service.get_chocolate_by_id(chocolate_id)

    if not chocolate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chocolate with ID {chocolate_id} not found",
        )

    return chocolate


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Orders"],  # This endpoint shows under "Orders" in the fast api docs
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Insufficient stock or invalid order",
        },
    },
)
async def create_order(order: OrderCreate) -> OrderResponse:
    """
    Create a new chocolate order.

    This shows a more complex endpoint that:
    - Takes a nested request body (order with multiple items)
    - Validates stock availability
    - Calculates totals
    - Returns a detailed response

    Args:
        order: Order data with customer info and items

    Returns:
        Created order with calculated total and status

    Raises:
        HTTPException: If insufficient stock or invalid data
    """
    try:
        order_dict = order.model_dump()
        created_order = await chocolate_service.create_order(order_dict)
        return created_order

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/inventory/low-stock",
    response_model=ChocolateResponse,
    responses={
        200: {"description": "List of low stock chocolates"},
    },
)
async def get_low_stock(threshold: Optional[int] = None):
    """ "
    Get the list of chocolates that are almost out of stock.

    Path parameters (like {threshold}) are extracted from the URL automatically.
    Example: GET /chocolates/inventory/low-stock/42 → threshold = 42

    Args:
        threshold: Stock quantity threshold (default: 10 units)

    Returns:
        List of chocolates needing restock with current quantities

    Raises:
        HTTPException: If no chocolates are low in stock
    """
    if threshold:
        chocolates = await chocolate_service.check_low_stock(threshold)
    else:
        chocolates = await chocolate_service.check_low_stock()

    if not chocolates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chocolates with stock amount under {threshold} were not found",
        )

    return chocolates


# To use this router in main.py, you'd do:
# from examples.example_router import router as chocolate_router
# app.include_router(chocolate_router)
