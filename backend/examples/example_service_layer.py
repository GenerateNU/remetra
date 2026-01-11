"""
Example service layer - Chocolate Shop Edition

The service layer sits between your API routes and your database.
Routes handle HTTP requests/responses, services handle the actual business logic.

This example shows:
- Input validation and business rules (checking stock, calculating prices)
- How to structure service methods (clear args, return values, error handling)
- Working with in-memory data (in the real app, you'd use a repository + database)

Note: This example uses in-memory data (fake chocolates list). In the real app,
you'd have a repository layer that talks to the database - see docs/ARCHITECTURE.md
"""

from datetime import datetime
from decimal import Decimal

# In-memory data for demonstration (pretend this is our database)
CHOCOLATES = [
    {
        "id": 1,
        "name": "Dark Chocolate Bar",
        "description": "70% cocoa dark chocolate",
        "price": Decimal("5.99"),
        "cocoa_percentage": 70,
        "stock_quantity": 50,
    },
    {
        "id": 2,
        "name": "Milk Chocolate Truffle",
        "description": "Creamy milk chocolate with hazelnut center",
        "price": Decimal("3.49"),
        "cocoa_percentage": 35,
        "stock_quantity": 5,  # Low stock!
    },
]

ORDERS = []  # Store orders here


class ChocolateService:
    """
    Service for handling chocolate shop business logic.

    This is where all the interesting stuff happens - validation, calculations,
    business rules. Routes just call these methods and return the results.
    """

    async def create_chocolate(self, chocolate_data: dict) -> dict:
        """
        Create a new chocolate product with validation.

        Business rules enforced:
        1. No duplicate names
        2. Price must be reasonable (under $100)
        3. Calculate shelf life based on cocoa percentage

        Args:
            chocolate_data: Validated data from ChocolateCreate model

        Returns:
            The created chocolate with generated ID and timestamps

        Raises:
            ValueError: If validation fails
        """
        if any(c["name"] == chocolate_data["name"] for c in CHOCOLATES):
            raise ValueError(f"Chocolate '{chocolate_data['name']}' already exists")

        # Dark chocolate lasts longer
        cocoa = chocolate_data.get("cocoa_percentage", 30)
        shelf_life_days = 365 if cocoa >= 70 else 180

        # Create the chocolate
        new_chocolate = {
            "id": len(CHOCOLATES) + 1,
            "shelf_life_days": shelf_life_days,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            **chocolate_data,  # ** unpacks the dictionary/json
            # we got from the create request, so we don't have to manually do it
        }

        CHOCOLATES.append(new_chocolate)
        return new_chocolate
