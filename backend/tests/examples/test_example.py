"""
Example tests demonstrating testing best practices.

Tests make sure your code works as expected and catches bugs before they reach production.
This example shows how to test service layer methods.

Key concepts:
- Test functions start with test_ so pytest can find them
- Arrange-Act-Assert pattern (setup data, run code, check results)
- Testing both success cases and error cases
- Using fixtures for reusable test data
"""

from decimal import Decimal

import pytest

from examples.example_service_layer import CHOCOLATES, ORDERS, ChocolateService


@pytest.fixture
def chocolate_service():
    """
    Fixture that provides a fresh ChocolateService for each test.

    Fixtures are reusable pieces of test setup that pytest manages.
    This runs before each test and provides a clean service instance.
    """
    return ChocolateService()


@pytest.fixture(autouse=True)
def reset_data():
    """
    Reset in-memory data before each test.

    autouse=True means this runs automatically before every test.
    This ensures tests don't interfere with each other.
    """
    # Clear and reset to original state
    CHOCOLATES.clear()
    CHOCOLATES.extend(
        [
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
                "stock_quantity": 5,
            },
        ]
    )
    ORDERS.clear()


class TestChocolateService:
    """
    Group related tests together in a class

    Classes help organize tests, will especially be helpful as the codebase expands
    All chocolate service tests go here.
    Pytest will find and run all test_ methods in this class so dw ab that
    """

    @pytest.mark.asyncio
    async def test_create_chocolate_success(self, chocolate_service):
        """
        Test creating a chocolate with valid data
        """
        chocolate_data = {
            "name": "White Chocolate Bar",
            "description": "Smooth white chocolate",
            "price": Decimal("4.99"),
            "cocoa_percentage": 0,
            "quantity": 100,
        }

        result = await chocolate_service.create_chocolate(chocolate_data)

        # Assert statements to verify expected outputs
        assert result["name"] == "White Chocolate Bar"
        assert result["price"] == Decimal("4.99")
        assert result["id"] == 3  # Should be next ID
        assert result["shelf_life_days"] == 180  # Low cocoa %

    @pytest.mark.asyncio
    async def test_create_chocolate_duplicate_name(self, chocolate_service):
        """
        Test that creating a chocolate with duplicate name fails (error case).

        Testing error cases is just as important
        """
        chocolate_data = {
            "name": "Dark Chocolate Bar",
            "description": "Another dark chocolate",
            "price": Decimal("6.99"),
            "quantity": 50,
        }

        # Chocolate name already exists
        with pytest.raises(ValueError) as exc_info:
            await chocolate_service.create_chocolate(chocolate_data)

        # Check the error message is what we expect
        assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_order_success(self, chocolate_service):
        """
        Test creating an order with valid items and sufficient stock
        """
        order_data = {
            "customer_name": "Alice",
            "items": [
                {"chocolate_id": 1, "quantity": 2},
                {"chocolate_id": 2, "quantity": 1},
            ],
            "special_instructions": "Gift wrap please",
        }

        result = await chocolate_service.create_order(order_data)

        # Assert
        assert result["customer_name"] == "Alice"
        assert result["status"] == "pending"
        # 2 * $5.99 + 1 * $3.49 = $15.47, no discount (under $50)
        assert result["total_price"] == Decimal("15.47")
        assert len(result["items"]) == 2

        assert CHOCOLATES[0]["stock_quantity"] == 48  
        assert CHOCOLATES[1]["stock_quantity"] == 4   

    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(self, chocolate_service):
        """
        Test that ordering more than available stock fails.

        This tests for expected error cases.
        """
        order_data = {
            "customer_name": "Bob",
            "items": [
                {"chocolate_id": 2, "quantity": 10},  # Only 5 in stock...
            ],
        }

        # Expecting an error as we are ordering tm
        with pytest.raises(ValueError) as exc_info:
            await chocolate_service.create_order(order_data)

        assert "Insufficient stock" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_check_low_stock(self, chocolate_service):
        """
        Test the low stock alert functionality.

        This test verifies we correctly identify products needing restock.
        """
        # Act - check for items below threshold of 10
        low_stock = await chocolate_service.check_low_stock(threshold=10)

        # Assert - only chocolate ID 2 should be low (quantity: 5)
        assert len(low_stock) == 1
        assert low_stock[0]["id"] == 2
        assert low_stock[0]["current_stock"] == 5
        assert low_stock[0]["recommended_order"] == 20  # 2x threshold


# Run tests with: just test
# or: docker compose run --rm backend pytest tests/
