"""Signal check: regenerates the users in the truth file and measures, from their logged meals and symptoms
alone, how often each trigger's symptom follows a meal containing it.

Usage (from backend/):
    python -m scripts.mock_users.check
"""

import argparse
import json
import math
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from scripts.mock_users.generate import DEFAULT_TRUTH_PATH, generate_users
from scripts.mock_users.shapes import MockUserData, Trigger, load_user_types
from scripts.mock_users.symptoms import BACKGROUND_SYMPTOMS, trigger_meals

STANDS_OUT_RATE = 0.4
MIN_MEALS_TO_JUDGE = 5


@dataclass(frozen=True)
class Signal:
    component: str
    trigger_meals: int
    followed: int  # trigger meals followed by the trigger's symptom inside its delay window
    by_chance: float  # chance a background symptom alone lands inside one delay window

    @property
    def follow_rate(self) -> float | None:
        return self.followed / self.trigger_meals if self.trigger_meals else None

    @property
    def judged(self) -> bool:
        return self.trigger_meals >= MIN_MEALS_TO_JUDGE

    @property
    def stands_out(self) -> bool:
        return self.judged and self.follow_rate >= STANDS_OUT_RATE


@dataclass(frozen=True)
class UserReport:
    username: str
    user_type: str
    signal: Signal  # the user's own trigger, or for no-trigger users the strongest of all triggers
    problem: str | None


def chance_by_background(trigger: Trigger, background_rate: float) -> float:
    per_hour = background_rate / len(BACKGROUND_SYMPTOMS) / 24
    return 1 - math.exp(-per_hour * (trigger.delay_max_hours - trigger.delay_min_hours))


def measure(user: MockUserData, trigger: Trigger, background_rate: float) -> Signal:
    meals = trigger_meals(user.meals, user.foods, trigger.component)
    low, high = timedelta(hours=trigger.delay_min_hours), timedelta(hours=trigger.delay_max_hours)
    times = [s.timestamp for s in user.symptoms if s.symptom == trigger.symptom]
    followed = sum(any(low <= t - meal.timestamp <= high for t in times) for meal in meals)
    return Signal(trigger.component, len(meals), followed, chance_by_background(trigger, background_rate))


def assess_users(users: list[MockUserData], triggers: list[Trigger], background_rate: float) -> list[UserReport]:
    """Trigger users must stand out for their own trigger. No-trigger users must not stand out for any trigger."""
    reports = []
    for user in users:
        own = user.user_type.trigger
        if own:
            signal = measure(user, own, background_rate)
            problem = None if signal.stands_out or not signal.judged else "trigger does not stand out"
        else:
            signals = [measure(user, t, background_rate) for t in triggers]
            signal = max(signals, key=lambda s: (s.judged, s.follow_rate or 0))
            problem = f"{signal.component} stands out for a no-trigger user" if signal.stands_out else None
        reports.append(UserReport(user.username, user.user_type.name, signal, problem))
    return reports


def _line(report: UserReport) -> str:
    s = report.signal
    rate = "n/a" if s.follow_rate is None else f"{s.follow_rate:.0%}"
    note = "" if s.judged else "  (too few trigger meals to judge)"
    return (
        f"{report.username}  {report.user_type:<13} {s.component:<16} trigger meals {s.trigger_meals:>3}  "
        f"followed {rate:>4}  by chance {s.by_chance:.1%}{note}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check that planted triggers stand out from background symptoms.")
    parser.add_argument("--truth", type=Path, default=DEFAULT_TRUTH_PATH, help="truth file written by the generator")
    args = parser.parse_args(argv)

    if not args.truth.exists():
        print(f"No truth file at {args.truth}. Run `just mock` first.")
        return 1
    truth = json.loads(args.truth.read_text(encoding="utf-8"))
    user_types, background_rate = load_user_types()
    users = generate_users(
        truth["seed"],
        len(truth["users"]),
        date.fromisoformat(truth["end_date"]),
        truth["days"],
        user_types=user_types,
        background_rate=background_rate,
    )
    triggers = [t.trigger for t in user_types.values() if t.trigger]
    reports = assess_users(users, triggers, background_rate)

    for report in reports:
        print(_line(report))
    failed = [r for r in reports if r.problem]
    if failed:
        print("Signal check failed:")
        for report in failed:
            print(f"  {report.username}: {report.problem}")
        return 1
    print(f"Signal check passed for {len(reports)} users")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
