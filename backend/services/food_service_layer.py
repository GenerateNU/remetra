# temporary database
FOODS = []


class FoodService:
    async def create_food(self, food_data: dict) -> dict:
        name = food_data.get("name")
        ingredients = food_data.get("ingredients")

        new_food = {
            "id": len(FOODS) + 1,
            "name": name,
            "ingredients": ingredients**food_data,
        }

        # replace FOODS with database stuff
        FOODS.append(new_food)
        return new_food

    async def get_foods(self) -> list[dict]:
        foods = list(FOODS)
        return foods

    async def get_by_food_id(self, id: int) -> dict:
        for food in FOODS:
            if food["id"] == id:
                return food
        return None

    async def update_food(self, id: int, name: str = None, ingredients: list[str] = None) -> dict:
        food = self.get_by_food_id(id)
        if name is not None:
            food.name = name
        if ingredients is not None:
            food.ingredients = ingredients

        return food

    async def delete_food(self, id: int):
        self.get_by_food_id(id)
        # add delete stuff databse
