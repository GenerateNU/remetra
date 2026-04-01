"""
Seed script: loads CSV data into the backend for a given user, then runs the algorithm.

Usage (from repo root, with backend venv active):
    python data_generator/seed.py                  # seeds user_001 (default)
    python data_generator/seed.py --user user_003  # seeds a specific user
    python data_generator/seed.py --all            # seeds all 40 users

Requires the FastAPI backend to be running at http://localhost:8000.
"""

import argparse
import ast
import csv
import sys
from pathlib import Path

import requests

BASE_URL = "http://localhost:8000"
DATA_DIR = Path(__file__).parent

MEALS_CSV = DATA_DIR / "step1_meals_logged.csv"
SYMPTOMS_CSV = DATA_DIR / "step3_symptoms_logged.csv"

# Symptom metadata: name → (location, sensation).
# The CSV only has symptom names; these are reasonable defaults.
SYMPTOM_META = {
    "bloating":    ("abdomen", "pressure"),
    "gas":         ("abdomen", "cramping"),
    "diarrhea":    ("abdomen", "urgency"),
    "constipation":("abdomen", "tightness"),
    "nausea":      ("stomach", "nausea"),
    "headache":    ("head", "throbbing"),
    "fatigue":     ("general", "tiredness"),
    "hives":       ("skin", "itching"),
    "rash":        ("skin", "irritation"),
    "reflux":      ("chest", "burning"),
    "cramping":    ("abdomen", "cramping"),
    "vomiting":    ("stomach", "nausea"),
    "itching":     ("skin", "itching"),
    "sneezing":    ("nose", "irritation"),
    "runny nose":  ("nose", "dripping"),
}


def signup_or_login(username: str) -> str:
    """Register the user, or log in if they already exist. Returns the access token."""
    resp = requests.post(f"{BASE_URL}/auth/signup", json={
        "username": username,
        "email": f"{username}@seed.example.com",
        "password": "seedpassword123",
    })
    if resp.status_code == 201:
        print(f"  Registered {username}")
        return resp.json()["access_token"]

    # 400 = username/email already exists → just log in
    if resp.status_code == 400:
        login = requests.post(f"{BASE_URL}/auth/login", json={
            "username": username,
            "password": "seedpassword123",
        })
        if login.status_code != 200:
            print(f"  ERROR: could not log in as {username}: {login.text}")
            sys.exit(1)
        print(f"  Logged in as {username} (already exists)")
        return login.json()["access_token"]

    print(f"  ERROR during signup: {resp.status_code} {resp.text}")
    sys.exit(1)


def seed_foods(token: str, food_rows: list[dict]) -> dict[str, str]:
    """
    Create food items for each unique food_name in the rows.
    Returns a mapping of food_name → backend UUID.
    """
    headers = {"Authorization": f"Bearer {token}"}

    # Collect unique (food_name, ingredients) pairs from the CSV
    seen: dict[str, list[str]] = {}
    for row in food_rows:
        name = row["food_name"].strip()
        if name in seen:
            continue
        raw_tags = row.get("tags", "[]")
        try:
            tags = ast.literal_eval(raw_tags)
        except Exception:
            tags = []
        seen[name] = tags

    food_map: dict[str, str] = {}
    created = skipped = 0

    for name, ingredients in seen.items():
        resp = requests.post(f"{BASE_URL}/food/", json={
            "name": name,
            "ingredients": ingredients,
        }, headers=headers)
        if resp.status_code == 201:
            food_map[name] = resp.json()["id"]
            created += 1
        else:
            # Already exists or error — try to find it by fetching all
            pass

    # Fetch all foods and fill in anything we missed
    all_foods = requests.get(f"{BASE_URL}/food/", headers=headers).json()
    for f in all_foods:
        if f["name"] in seen and f["name"] not in food_map:
            food_map[f["name"]] = f["id"]
            skipped += 1

    print(f"  Foods: {created} created, {skipped} already existed — {len(food_map)} total mapped")
    return food_map


def seed_symptoms(token: str, symptom_names: set[str]) -> dict[str, str]:
    """
    Create symptom items for each unique symptom name.
    Returns a mapping of symptom_name → backend UUID.
    """
    headers = {"Authorization": f"Bearer {token}"}
    symptom_map: dict[str, str] = {}
    created = skipped = 0

    for name in symptom_names:
        meta = SYMPTOM_META.get(name, ("general", "discomfort"))
        resp = requests.post(f"{BASE_URL}/symptom/", json={
            "name": name,
            "location": meta[0],
            "sensation": meta[1],
        }, headers=headers)
        if resp.status_code == 201:
            symptom_map[name] = resp.json()["id"]
            created += 1
        else:
            pass

    # Fill in any that already existed
    all_symptoms = requests.get(f"{BASE_URL}/symptom/", headers=headers).json()
    for s in all_symptoms:
        if s["name"] in symptom_names and s["name"] not in symptom_map:
            symptom_map[s["name"]] = s["id"]
            skipped += 1

    print(f"  Symptoms: {created} created, {skipped} already existed — {len(symptom_map)} total mapped")
    return symptom_map


def seed_food_logs(token: str, username: str, food_rows: list[dict], food_map: dict[str, str]):
    headers = {"Authorization": f"Bearer {token}"}
    ok = skipped = errors = 0

    for row in food_rows:
        name = row["food_name"].strip()
        food_id = food_map.get(name)
        if not food_id:
            skipped += 1
            continue
        resp = requests.post(f"{BASE_URL}/food-log/", json={
            "food_id": food_id,
            "username": username,
            "timestamp": row["timestamp"].replace(" ", "T"),
            "quantity": row.get("meal_type"),  # reuse meal_type as a rough quantity label
        }, headers=headers)
        if resp.status_code == 201:
            ok += 1
        else:
            errors += 1

    print(f"  Food logs: {ok} created, {skipped} skipped (unmapped food), {errors} errors")


def seed_symptom_logs(token: str, username: str, symptom_rows: list[dict], symptom_map: dict[str, str]):
    headers = {"Authorization": f"Bearer {token}"}
    ok = skipped = errors = 0

    for row in symptom_rows:
        name = row["symptom"].strip()
        symptom_id = symptom_map.get(name)
        if not symptom_id:
            skipped += 1
            continue
        intensity = int(float(row["severity"]))
        intensity = max(1, min(10, intensity))  # clamp to 1–10

        resp = requests.post(f"{BASE_URL}/symptom-logs/", json={
            "symptom_id": symptom_id,
            "username": username,
            "intensity": intensity,
            "timestamp": row["timestamp"].replace(" ", "T"),
        }, headers=headers)
        if resp.status_code == 201:
            ok += 1
        else:
            errors += 1

    print(f"  Symptom logs: {ok} created, {skipped} skipped (unmapped symptom), {errors} errors")


def run_algorithm(token: str, username: str):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/algorithm/run", json={"user_id": username}, headers=headers)
    if resp.status_code == 200:
        associations = resp.json().get("associations", [])
        print(f"  Algorithm ran — {len(associations)} associations produced")
    else:
        print(f"  ERROR running algorithm: {resp.status_code} {resp.text}")


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def seed_user(username: str):
    print(f"\n=== Seeding {username} ===")

    all_meal_rows = read_csv(MEALS_CSV)
    all_symptom_rows = read_csv(SYMPTOMS_CSV)

    meal_rows = [r for r in all_meal_rows if r["user_id"] == username]
    symptom_rows = [r for r in all_symptom_rows if r["user_id"] == username]

    print(f"  Data: {len(meal_rows)} food logs, {len(symptom_rows)} symptom logs")

    token = signup_or_login(username)
    food_map = seed_foods(token, meal_rows)
    symptom_names = {r["symptom"].strip() for r in symptom_rows}
    symptom_map = seed_symptoms(token, symptom_names)
    seed_food_logs(token, username, meal_rows, food_map)
    seed_symptom_logs(token, username, symptom_rows, symptom_map)
    run_algorithm(token, username)

    print(f"=== Done: {username} ===")


def main():
    parser = argparse.ArgumentParser(description="Seed Remetra backend with CSV data")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--user", default="user_001", help="Single user to seed (default: user_001)")
    group.add_argument("--all", action="store_true", help="Seed all 40 users")
    args = parser.parse_args()

    # Quick health check
    try:
        requests.get(f"{BASE_URL}/food/", timeout=3)
    except Exception:
        print(f"ERROR: Backend not reachable at {BASE_URL}. Is it running?")
        sys.exit(1)

    if args.all:
        users = [f"user_{str(i).zfill(3)}" for i in range(1, 41)]
        for user in users:
            seed_user(user)
    else:
        seed_user(args.user)


if __name__ == "__main__":
    main()
