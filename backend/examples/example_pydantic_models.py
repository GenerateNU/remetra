"""
Example data models for API requests and responses - Chocolate Shop example (I couldn't come up w/anything else)!

Models define the shape and validation rules for data coming into and out of the API.
Think of them as contracts - they ensure data is structured correctly and validate types.

Key concepts:
- Request models: Data the client/user/idk sends to us (e.g., when creating a chocolate order)
- Response models: Data we send back to the frontend (e.g., the created order with ID)
- Field validation: Automatic checking of data types, ranges, and constraints
- Field descriptions: Show up in API docs (/docs, /scalar) to help API consumers and future developers!
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ChocolateBase(BaseModel):
    """
    Common chocolate fields used in both requests and responses.

    We define shared fields once here, then reuse them in other models (Abstracted out so we don't repeat ourselves)
    """

    name: str = Field(
        ...,  # by adding ... you make it a required field
        description="Name of the chocolate (e.g., 'Dark Chocolate Bar (THE BEST TYPE)', 'Milk Chocolate Bar')",
        min_length=1,
        max_length=100,
    )
    description: str = Field(
        ...,
        description="Description of the chocolate (strength of cacao, mix ins etc.)",
        max_length=500,
    )
    price: Decimal = Field(
        ...,
        description="Price in USD",
        ge=0.01,  # Must be at least 1 cent
        decimal_places=2,  # Ensures proper money format
    )
    cocoa_percentage: Optional[int] = Field(
        None,  # None makes this field optional
        description="Percentage of cocoa content (e.g., 70 for 70% dark chocolate)",
        ge=0,
        le=100,
    )


class ChocolateCreate(ChocolateBase):
    """
    Data structure for creating a new chocolate product

    Used when a client sends a POST request to add a new chocolate to inventory.
    Inherits all fields from ChocolateBase
    """

    quantity: int = Field(
        ...,
        description="Initial stock quantity",
        ge=0,  # Can't have negative stock
    )


class ChocolateResponse(ChocolateBase):
    """
    Data structure for chocolate responses sent back to clients.

    Includes the original chocolate data plus new fields
    like ID, timestamps, and current stock that the database tracks automatically.
    """

    model_config = ConfigDict(from_attributes=True)  # Allows loading from database models (SQLAlchemy)

    id: int = Field(..., description="Unique ID for this chocolate product")
    stock_quantity: int = Field(..., description="Current stock quantity")
    created_at: datetime = Field(..., description="When this product was first added")
    updated_at: datetime = Field(..., description="When this product was last modified")


class OrderItemBase(BaseModel):
    """
    Individual item within an order (a specific chocolate and quantity).
    """

    chocolate_id: int = Field(..., description="ID of the chocolate being ordered")
    quantity: int = Field(
        ...,
        description="Number of units to order",
        ge=1,  # Must order at least 1
    )


class OrderCreate(BaseModel):
    """
    Data structure for creating a new order.

    An order can contain multiple chocolate item objects
    """

    customer_name: str = Field(
        ...,
        description="Name of the customer placing the order",
        min_length=1,
        max_length=100,
    )
    items: list[OrderItemBase] = Field(
        ...,
        description="List of chocolates and quantities being ordered",
        min_length=1,  # Order must have at least one item
    )
    special_instructions: Optional[str] = Field(
        None,
        description="Any special packaging or delivery instructions",
        max_length=500,
    )


class OrderResponse(BaseModel):
    """
    Data structure for order responses sent back to clients.

    Includes order details, calculated totals, and system-generated fields.
    """

    model_config = ConfigDict(from_attributes=True)
    # Lets Pydantic work with database models directly
    # When we fetch a chocolate from the database (SQLAlchemy), it comes back as an object
    # with attributes like chocolate.name and chocolate.price (not a dict / json)
    # This setting tells Pydantic "read from object.attribute instead of dict['key']"
    # so we can convert database objects to API responses without manual mapping

    id: int = Field(..., description="Unique order ID")
    customer_name: str = Field(..., description="Customer name")
    items: list[OrderItemBase] = Field(..., description="Ordered items")
    total_price: Decimal = Field(..., description="Total order price (calculated)")
    status: str = Field(..., description="Order status (pending/completed/cancelled)")
    created_at: datetime = Field(..., description="When the order was placed")


class LowStockResponse(BaseModel):
    """
    Data structure for low stock alert responses.

    Returned when checking inventory levels to identify products that need restocking.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique ID of the chocolate product")
    name: str = Field(..., description="Name of the chocolate product")
    current_stock: int = Field(..., description="Current stock quantity")
    recommended_order: int = Field(..., description="Recommended quantity to reorder")


class ErrorResponse(BaseModel):
    """
    Standard format for error messages.

    When something goes wrong (e.g., insufficient stock, invalid ID),
    we send this back with a clear explanation to help with debugging!
    """

    detail: str = Field(..., description="What went wrong")
    error_code: Optional[str] = Field(
        None,
        description="Optional machine-readable error code for programmatic handling",
    )
