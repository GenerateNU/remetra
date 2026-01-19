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

    async def get_chocolates(
        self,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock_only: bool = False,
    ) -> list[dict]:
        """
        Get chocolates with optional filtering.

        Business logic:
        - Filter by price range if specified
        - Optionally show only in-stock items
        - Sort by price (low to high)

        Args:
            min_price: Minimum price filter (optional)
            max_price: Maximum price filter (optional)
            in_stock_only: If True, only return chocolates with stock > 0

        Returns:
            List of chocolate dictionaries matching the filters
        """
        chocolates = list(CHOCOLATES)  # Copy the list

        # Apply filters based on parameters
        if min_price:
            chocolates = [c for c in chocolates if c["price"] >= min_price]
        if max_price:
            chocolates = [c for c in chocolates if c["price"] <= max_price]
        if in_stock_only:
            chocolates = [c for c in chocolates if c["stock_quantity"] > 0]

        chocolates.sort(key=lambda c: c["price"])

        return chocolates

    async def get_chocolate_by_id(self, chocolate_id: int) -> dict | None:
        """
        Get a specific chocolate by its ID.

        Args:
            chocolate_id: Unique identifier for the chocolate

        Returns:
            Chocolate dictionary if found, None if not found
        """
        for chocolate in CHOCOLATES:
            if chocolate["id"] == chocolate_id:
                return chocolate
        return None

    async def create_order(self, order_data: dict) -> dict:
        """
        Process a new order with inventory checks and price calculation.

        Business rules:
        1. Check stock availability for all items
        2. Calculate total price (sum of item_price * quantity)
        3. Apply bulk discount if order total > $50 (10% off)
        4. Create order record

        Args:
            order_data: Validated data from OrderCreate model

        Returns:
            Created order with calculated total and status

        Raises:
            ValueError: If insufficient stock for any item or chocolate not found
        """
        items = order_data["items"]
        total_price = Decimal("0.00")

        for item in items:
            chocolate = await self.get_chocolate_by_id(item["chocolate_id"])

            if not chocolate:
                raise ValueError(f"Chocolate ID {item['chocolate_id']} not found")

            if chocolate["stock_quantity"] < item["quantity"]:
                raise ValueError(
                    f"Insufficient stock for '{chocolate['name']}'. "
                    f"Available: {chocolate['stock_quantity']}, "
                    f"Requested: {item['quantity']}"
                )

            item_total = chocolate["price"] * item["quantity"]
            total_price += item_total
            # Deduct stock
            chocolate["stock_quantity"] -= item["quantity"]

        if total_price > Decimal("50.00"):
            total_price *= Decimal("0.90")  # 10% off

        order = {
            "id": len(ORDERS) + 1,
            "customer_name": order_data["customer_name"],
            "items": items,
            "total_price": total_price,
            "status": "pending",
            "created_at": datetime.now(),
        }

        ORDERS.append(order)
        return order

    async def check_low_stock(self, threshold: int = 10) -> list[dict]:
        """
        Find chocolates with low inventory for restocking alerts.

        Business logic: Identify products below restock threshold
        so the shop can reorder before running out.

        Args:
            threshold: Stock quantity threshold (default: 10 units)

        Returns:
            List of chocolates needing restock with current quantities
        """
        low_stock = [
            {
                "id": c["id"],
                "name": c["name"],
                "current_stock": c["stock_quantity"],
                "recommended_order": threshold * 2,  # Restock to 2x threshold
            }
            for c in CHOCOLATES
            if c["stock_quantity"] < threshold
        ]

        return low_stock
