"""
Food library mock users pick their regular foods from, grouped by when people eat them.
"""

from scripts.mock_users.shapes import MockFood

FOODS_BY_SLOT: dict[str, list[MockFood]] = {
    "breakfast": [
        MockFood("Oatmeal with blueberries", ["oatmeal", "blueberries", "maple syrup"]),
        MockFood("Oatmeal with milk and banana", ["oatmeal", "milk", "banana"]),
        MockFood("Yogurt and granola", ["yogurt", "granola", "strawberries"]),
        MockFood("Scrambled eggs on toast", ["eggs", "butter", "wheat bread"]),
        MockFood("Veggie omelette", ["eggs", "onion", "bell pepper", "spinach", "olive oil"]),
        MockFood("Bagel with cream cheese", ["bagels", "fresh cheese"]),
        MockFood("Peanut butter toast", ["whole wheat bread", "peanut butter", "banana"]),
        MockFood("Avocado toast", ["wheat bread", "avocado", "lemon juice", "salt"]),
        MockFood("Breakfast burrito", ["flour tortillas", "eggs", "cheese", "onion", "tomato"]),
        MockFood("Fruit smoothie", ["banana", "strawberries", "almond milk"]),
    ],
    "lunch": [
        MockFood("Turkey sandwich", ["wheat bread", "turkey breast", "lettuce", "tomato", "mayonnaise"]),
        MockFood("Grilled cheese", ["wheat bread", "cheese", "butter"]),
        MockFood("Chicken caesar salad", ["romaine", "chicken breast", "parmesan", "garlic", "lemon juice"]),
        MockFood("Quinoa salad", ["quinoa", "cucumber", "cherry tomatoes", "olive oil", "lemon juice"]),
        MockFood("Chicken and rice bowl", ["chicken breast", "white rice", "broccoli", "soy sauce"]),
        MockFood("Lentil soup", ["lentils", "carrots", "celery", "onion", "garlic", "vegetable broth"]),
        MockFood("Tuna salad sandwich", ["canned tuna", "mayonnaise", "celery", "wheat bread"]),
        MockFood("Hummus wrap", ["flour tortillas", "hummus", "cucumber", "lettuce"]),
        MockFood("Tomato soup and crackers", ["tomato sauce", "onion", "heavy cream", "crackers"]),
        MockFood("Mac and cheese", ["pasta", "cheese", "milk", "butter"]),
    ],
    "dinner": [
        MockFood("Spaghetti with marinara", ["pasta", "tomato sauce", "garlic", "onion", "olive oil"]),
        MockFood("Grilled salmon with rice", ["salmon", "brown rice", "green beans", "lemon", "olive oil"]),
        MockFood("Chicken stir fry", ["chicken breast", "bell pepper", "broccoli", "soy sauce", "fresh ginger"]),
        MockFood("Beef tacos", ["ground beef", "corn tortillas", "onion", "cheese", "taco seasoning"]),
        MockFood("Steak and potatoes", ["steak", "potato", "butter", "salt"]),
        MockFood("Chicken curry", ["chicken breast", "curry sauce", "onion", "garlic", "white rice"]),
        MockFood("Tofu and veggie bowl", ["tofu", "white rice", "bok choy", "carrots", "tamari"]),
        MockFood("Pesto pasta", ["pasta", "pesto", "parmesan"]),
        MockFood("Baked cod with vegetables", ["cod", "zucchini", "carrots", "olive oil", "salt"]),
        MockFood("Pepperoni pizza", ["pizza dough", "tomato sauce", "cheese", "pepperoni"]),
        MockFood("Fettuccine alfredo", ["pasta", "cream sauce", "parmesan", "garlic"]),
    ],
    "snack": [
        MockFood("Apple and peanut butter", ["apple", "peanut butter"]),
        MockFood("Trail mix", ["trail mix"]),
        MockFood("Cheese and crackers", ["cheese", "crackers"]),
        MockFood("Ice cream", ["ice cream"]),
        MockFood("Chips and guacamole", ["corn tortillas", "guacamole"]),
        MockFood("Carrots and hummus", ["carrots", "hummus"]),
        MockFood("Popcorn", ["popcorn", "butter", "salt"]),
        MockFood("Grapes", ["grapes"]),
        MockFood("Dark chocolate", ["dark chocolate"]),
    ],
    "drink": [
        MockFood("Black coffee", ["coffee"]),
        MockFood("Latte", ["espresso", "milk"]),
        MockFood("Green tea", ["green tea"]),
        MockFood("Orange juice", ["orange juice"]),
        MockFood("Sparkling water", ["sparkling water"]),
        MockFood("Glass of red wine", ["red wine"]),
        MockFood("Glass of white wine", ["white wine"]),
        MockFood("Beer", ["beer"]),
        MockFood("Margarita", ["tequila", "lime juice"]),
    ],
}
