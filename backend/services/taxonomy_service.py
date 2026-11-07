import csv
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "taxonomy" / "ingredient_components.csv"


def get_components(ingredient: str) -> list[dict]:
    """Return all components (with concentration) for an ingredient, matched by ingredient_id or canonical_name."""
    key = ingredient.strip().lower()
    with open(CSV_PATH, newline="") as f:
        return [
            {"component": row["component"], "concentration_level": int(row["concentration_level"])}
            for row in csv.DictReader(f)
            if key in (row["ingredient_id"].lower(), row["canonical_name"].lower())
        ]


if __name__ == "__main__":
    print(get_components("wheat_bread"))