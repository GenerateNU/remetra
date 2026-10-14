"""
Filter food.com recipes from Kaggle dataset to only include recipes that are anti-inflammatory. Also only get top 100.
"""

import re

import pandas as pd

TARGET_COUNT = 100
MIN_GOOD_INGREDIENTS = 3
MIN_AVG_RATING = 4.8 
MIN_NUM_RATINGS = 100
EXCLUDE_TAGS = {"candy", "cocktails"}
OUTPUT_FILE = "backend/data/raw/foodrecipes/v1_recipe_scraping_output.csv"

GOOD = [
    "salmon", "sardine", "mackerel", "trout", "tuna", "anchov",
    "olive oil", "avocado", "walnut", "almond", "flax", "chia",
    "spinach", "kale", "swiss chard", "arugula", "collard",
    "broccoli", "brussels sprout", "cabbage", "cauliflower",
    "tomato", "bell pepper", "sweet potato", "carrot", "beet",
    "lentil", "chickpea", "garbanzo", "black bean", "kidney bean",
    "white bean", "cannellini", "quinoa", "oat", "brown rice", "barley",
    "blueberr", "strawberr", "raspberr", "blackberr", "cherr",
    "turmeric", "ginger", "garlic", "cinnamon", "green tea", "mushroom",
]
 
BAD = [
    "bacon", "sausage", "ham", "pepperoni", "salami", "hot dog",
    "bologna", "chorizo", "spam", "corn syrup", "margarine",
    "shortening", "white bread", "cake mix", "frosting", "marshmallow",
    "processed cheese", "velveeta",
]
 
BAD_STEP_PHRASES = ["deep fry", "deep-fry", "deep fat", "deep-fat"]

# so that oat and oatmeal is included but not goat
GOOD_PATTERNS = [re.compile(r"\b" + re.escape(g)) for g in GOOD]
BAD_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(b) for b in BAD) + r")(s|es)?\b"
)

def parse_r_vector(value):
    """
    This dataset stores lists in R format, e.g. c("kale", "garlic") so need to parse it.
    """
    if not isinstance(value, str):
        return []
    return re.findall(r'"([^"]*)"', value)

def count_good(ingredients):
    """Counts number of good ingredients in recipe"""
    text = " | ".join(ingredients).lower()
    return sum(1 for p in GOOD_PATTERNS if p.search(text))
 
 
def has_bad(ingredients):
    """Checks if recipe contains any bad ingredients"""
    return bool(BAD_PATTERN.search(" | ".join(ingredients).lower()))
 
 
def has_bad_steps(steps):
    """Checks if recipe contains any bad steps"""
    text = " ".join(steps).lower()
    return any(p in text for p in BAD_STEP_PHRASES)
 
 
def is_excluded_category(category, keywords):
    """Checks if recipe belongs to an excluded category or contains excluded keywords"""
    cat = str(category).lower()
    if any(w in cat for w in EXCLUDE_TAGS):
        return True
    return bool(EXCLUDE_TAGS & set(keywords))
 
 
def make_url(row):
    """Generates the URL for a given recipe row"""
    snake = re.sub(r"[^a-z0-9]+", "-", str(row["Name"]).lower().replace("'", "")).strip("-")
    return f"https://www.food.com/recipe/{snake}-{row['RecipeId']}"

def main():
    cols = ["RecipeId", "Name", "RecipeCategory", "Keywords",
            "RecipeIngredientParts", "RecipeInstructions", "AggregatedRating",
            "ReviewCount"]
    df = pd.read_csv("backend/data/raw/foodrecipes/recipes.csv", usecols=cols)
 
    df["ingredients"] = df["RecipeIngredientParts"].apply(parse_r_vector)
    df["steps"] = df["RecipeInstructions"].apply(parse_r_vector)
    df["keywords"] = df["Keywords"].apply(parse_r_vector)
    for c in ["AggregatedRating", "ReviewCount"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
 
    df["good_count"] = df["ingredients"].apply(count_good)
    good_recipes = (
        (df["good_count"] >= MIN_GOOD_INGREDIENTS)
        & ~df["ingredients"].apply(has_bad)
        & ~df["steps"].apply(has_bad_steps)
        & ~df.apply(lambda r: is_excluded_category(r["RecipeCategory"], r["keywords"]), axis=1)
    )

    good_recipes &= (df["AggregatedRating"] >= MIN_AVG_RATING) & (df["ReviewCount"] >= MIN_NUM_RATINGS)
 
    result = df[good_recipes].sort_values(
        ["good_count", "AggregatedRating", "ReviewCount"], ascending=False
    ).head(TARGET_COUNT).copy()
 
    result["name"] = result["Name"]
    result["url"] = result.apply(make_url, axis=1)
    result["ingredients"] = result["ingredients"].apply(", ".join)
    result[["name", "url", "ingredients"]].to_csv(OUTPUT_FILE, index=False)
 
if __name__ == "__main__":
    main()