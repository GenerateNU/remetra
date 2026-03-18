from models import FoodLogEntry

def count_ingredient_occurrences(
    food_logs: list[FoodLogEntry],
) ->  tuple[dict[str, int], int]:
    """Returns (ingredient_counts, total_food_events)."""
    
    ingredient_counts: dict[str, int] = {}

    for log in food_logs:
        for ingredient in set(log.ingredients):
            ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1
    
    total_food_events = len(food_logs)
    return (ingredient_counts, total_food_events)   
