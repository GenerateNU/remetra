# Mock users

Fills the database with realistic `mock_` users. Each user gets 60 days of meals, symptoms, and Apple Health rows (sleep, HRV, resting heart rate) ending today, and the same seed always gives the same data. User types come from `user_types.yaml`: one planted trigger (onion and garlic, lactose, or alcohol) or no trigger.

```bash
just mock
just mock 8 7 90 # 8 users, seed 7, 90 days
just mock-check
just mock-clear
```

`just mock` replaces existing `mock_` users and never touches other accounts. After saving, it writes `output/truth.json` with each user's type and planted trigger. `just mock-check` regenerates the users in `truth.json` and, using only their logged meals and symptoms, reports how many meals contained each trigger and how often the trigger's symptom followed inside its delay window. It also shows how often that would happen by chance from background symptoms. A trigger user stands out when at least 40% of their trigger meals are followed. A no-trigger user must not stand out for any trigger. Users with fewer than 5 trigger meals are listed but not judged.
