"""Seed ~45 days of realistic Apple Health data (+ matching symptom logs) for one user, then verify
the edge cases the Health Trends chart has to handle.

Goes through the same validation (HealthSyncRequest) and service (HealthSyncService) as
POST /health/sync — only the HTTP/Clerk auth layer is skipped.

How to run:
    1. Start the stack with `just dev`, sign up in the app and finish onboarding, so the user exists.
    
    2. From the repo root, with the stack running:

        docker compose exec backend python scripts/seed_health_data.py --username <username>

       Remove the seeded data again:

        docker compose exec backend python scripts/seed_health_data.py --username <username> --clear-only

Options:
    --timezone America/New_York   timezone the "phone" syncs in (default America/New_York)
    --clear-only                  remove previously seeded data for the user and exit

Re-running is safe: seeded data for the user is cleared first, then re-created. Seeded symptom logs
are tagged "[health-seed]" in their notes, which is how they're found and cleared.
"""

import argparse
import random
import sys
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import ValidationError
from sqlalchemy import delete, select

import models.symptom  # noqa: F401
import models.symptom_log  # noqa: F401
import models.user  # noqa: F401
from auth_context import current_username
from database import SessionLocal
from models.daily_health_metrics import DailyHealthMetrics
from models.healthkit_event import HealthKitEvent
from models.symptom import Symptom
from models.symptom_log import SymptomLog
from models.user import User
from schemas.health import HealthSyncRequest
from services.health_sync_service import HealthSyncService

try:  # only on branches with GET /health/trends
    from services.health_trends_service import HealthTrendsService
except ModuleNotFoundError:
    HealthTrendsService = None

SEED_MARKER = "[health-seed]"
HK_NAMESPACE = uuid.UUID("6f1c2a52-3a1e-4d7a-9a51-1c0de5eed000")
TOTAL_DAYS = 45  # days 0..44 ago; the chart shows the last 30
CHART_DAYS = 30

# --- Scenario, in "days ago" -------------------------------------------------------------------
FLARE_DAYS = {24: 0.6, 23: 1.0, 22: 0.9, 12: 0.7, 11: 0.8, 3: 0.6}  # day -> severity 0..1
PRE_FLARE_DAYS = {25: 0.3, 13: 0.3, 4: 0.2}  # HRV starts dipping the day before symptoms
NO_ROW_DAYS = {18, 17, 16, 14}  # watch not worn: no row at all (15 becomes an isolated reading)
SLEEP_MISSING_DAYS = {6}  # watch charging overnight: HRV/RHR present, sleep null
HRV_MISSING_DAYS = {5}  # Apple didn't record HRV that day
EXTREMES = {22: dict(sleep=205, hrv=19.5, rhr=84.0), 21: dict(sleep=655)}  # flare peak + recovery sleep

SYMPTOMS = [  # (sensation, location)
    ("Fatigue", "General"),
    ("Bloating", "Abdomen"),
    ("Aching", "Joints"),
]
# day -> list of (symptom index, intensity, local hour, local minute)
SYMPTOM_LOGS = {
    24: [(0, 5, 9, 15)],
    23: [(0, 7, 8, 30), (2, 6, 18, 45)],  # two logs, one day -> one band, symptom_count 2
    22: [(0, 8, 10, 0)],
    17: [(1, 4, 13, 0)],  # symptom on a day with no health data
    12: [(1, 6, 20, 10)],
    11: [(1, 5, 7, 50)],
    8: [(2, 3, 23, 40)],  # late evening: must land on day 8 locally, not the next UTC day
    3: [(0, 4, 12, 0)],
    35: [(1, 6, 12, 0)],  # outside the 30-day window: must not appear
}
# HealthKit events (not drawn on the chart, but part of the sync payload)
HK_EVENTS = [  # (day, category, type, value, local hour, duration hours)
    (23, "symptom", "headache", "moderate", 15, 3),
    (22, "symptom", "fatigue", "severe", 8, 10),
    (11, "symptom", "bloating", "mild", 19, 2),
    (20, "menstrual_flow", "flow", "medium", 0, 24),
    (19, "menstrual_flow", "flow", "heavy", 0, 24),
    (18, "menstrual_flow", "flow", "medium", 0, 24),
    (17, "menstrual_flow", "flow", "light", 0, 24),
]


def build_days(today: date, rng: random.Random) -> list[dict]:
    hrv_base, rhr_base = 46.0, 59.0
    days = []
    for ago in range(TOTAL_DAYS - 1, -1, -1):
        d = today - timedelta(days=ago)
        if ago in NO_ROW_DAYS:
            continue

        stress = FLARE_DAYS.get(ago, PRE_FLARE_DAYS.get(ago, 0.0))
        weekend = d.weekday() >= 5

        # Sleep: ~7h, longer on weekends, shorter + more fragmented in flares
        total = rng.gauss(425 + (40 if weekend else 0) - 90 * stress, 25)
        total = int(max(240, min(600, total)))
        deep = int(total * rng.uniform(0.13, 0.18) * (1 - 0.3 * stress))
        rem = int(total * rng.uniform(0.20, 0.25))
        core = total - deep - rem
        awake = int(rng.uniform(12, 30) + 60 * stress)

        hrv = round(rng.gauss(hrv_base * (1 - 0.35 * stress), 4), 1)
        rhr = round(rng.gauss(rhr_base + 9 * stress, 1.5), 1)

        entry = dict(
            date=d.isoformat(),
            sleep_total_min=total,
            sleep_deep_min=deep,
            sleep_rem_min=rem,
            sleep_core_min=core,
            sleep_awake_min=awake,
            hrv_avg_ms=hrv,
            resting_hr_bpm=rhr,
        )

        ext = EXTREMES.get(ago, {})
        if "sleep" in ext:
            s = ext["sleep"]
            entry.update(
                sleep_total_min=s,
                sleep_deep_min=int(s * 0.12),
                sleep_rem_min=int(s * 0.22),
                sleep_core_min=s - int(s * 0.12) - int(s * 0.22),
                sleep_awake_min=95 if s < 300 else 20,
            )
        if "hrv" in ext:
            entry["hrv_avg_ms"] = ext["hrv"]
        if "rhr" in ext:
            entry["resting_hr_bpm"] = ext["rhr"]

        if ago in SLEEP_MISSING_DAYS:
            for k in ("sleep_total_min", "sleep_deep_min", "sleep_rem_min", "sleep_core_min", "sleep_awake_min"):
                entry[k] = None
        if ago in HRV_MISSING_DAYS:
            entry["hrv_avg_ms"] = None
        if ago == 0:  # today: last night's sleep is in, HRV/RHR not computed yet
            entry["hrv_avg_ms"] = None
            entry["resting_hr_bpm"] = None

        days.append(entry)
    return days


def build_events(today: date, tz: ZoneInfo, username: str) -> list[dict]:
    events = []
    for ago, category, type_, value, hour, hours in HK_EVENTS:
        d = today - timedelta(days=ago)
        start = datetime.combine(d, time(hour), tzinfo=tz)
        end = start + timedelta(hours=hours) - (timedelta(minutes=1) if hours == 24 else timedelta())
        events.append(
            dict(
                # deterministic per user/day/type, so re-syncs dedupe on hk_uuid like real HealthKit ids
                hk_uuid=str(uuid.uuid5(HK_NAMESPACE, f"{username}:{d}:{category}:{type_}")),
                category=category,
                type=type_,
                value=value,
                start_at=start.isoformat(),
                end_at=end.isoformat(),
                date=d.isoformat(),
            )
        )
    return events


def clear(db, username: str, today: date, events: list[dict]) -> None:
    first = today - timedelta(days=TOTAL_DAYS - 1)
    db.execute(
        delete(DailyHealthMetrics).where(
            DailyHealthMetrics.username == username,
            DailyHealthMetrics.date >= first,
            DailyHealthMetrics.date <= today,
        )
    )
    db.execute(
        delete(HealthKitEvent).where(
            HealthKitEvent.username == username,
            HealthKitEvent.hk_uuid.in_([uuid.UUID(e["hk_uuid"]) for e in events]),
        )
    )
    db.execute(delete(SymptomLog).where(SymptomLog.username == username, SymptomLog.notes == SEED_MARKER))
    db.commit()


def seed_symptom_logs(db, username: str, today: date, tz: ZoneInfo) -> int:
    symptoms = []
    for sensation, location in SYMPTOMS:
        name = f"{sensation} — {location}"
        s = db.execute(select(Symptom).where(Symptom.username == username, Symptom.name == name)).scalar_one_or_none()
        if not s:
            s = Symptom(username=username, name=name, sensation=sensation, location=location)
            db.add(s)
            db.flush()
        symptoms.append(s)

    count = 0
    for ago, logs in SYMPTOM_LOGS.items():
        d = today - timedelta(days=ago)
        for idx, intensity, hour, minute in logs:
            db.add(
                SymptomLog(
                    username=username,
                    symptom_id=symptoms[idx].id,
                    intensity=intensity,
                    timestamp=datetime.combine(d, time(hour, minute), tzinfo=tz),
                    notes=SEED_MARKER,
                )
            )
            count += 1
    db.commit()
    return count


class Checks:
    def __init__(self):
        self.failed = 0

    def __call__(self, ok: bool, label: str, detail: str = "") -> None:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}{f'  ({detail})' if detail and not ok else ''}")
        self.failed += 0 if ok else 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--timezone", default="America/New_York")
    parser.add_argument("--clear-only", action="store_true")
    args = parser.parse_args()

    tz = ZoneInfo(args.timezone)
    today = datetime.now(tz).date()
    username = args.username
    rng = random.Random(f"{username}:{today}")

    db = SessionLocal()
    ctx = current_username.set(username)  # act as the user, like an authenticated request
    try:
        if not db.get(User, username):
            existing = [u for (u,) in db.execute(select(User.username)).all()]
            sys.exit(
                f"User '{username}' not found. Sign up in the app first (finish onboarding).\n"
                f"Existing users: {', '.join(existing) or '(none)'}"
            )

        events = build_events(today, tz, username)
        clear(db, username, today, events)
        if args.clear_only:
            print(f"Cleared seeded health data for {username}.")
            return

        check = Checks()
        service = HealthSyncService()
        days = build_days(today, rng)

        print("Validation (bad payloads must be rejected before anything is saved):")
        bad_cases = {
            "sleep over 24h": dict(date=today.isoformat(), sleep_total_min=1500),
            "negative sleep": dict(date=today.isoformat(), sleep_deep_min=-5),
        }
        for label, bad_day in bad_cases.items():
            try:
                HealthSyncRequest(timezone=args.timezone, days=[bad_day], events=[])
                check(False, f"rejects {label}")
            except ValidationError:
                check(True, f"rejects {label}")
        try:
            HealthSyncRequest(timezone=args.timezone, days=[], events=[{**events[0], "value": "extreme"}])
            check(False, "rejects invalid symptom severity")
        except ValidationError:
            check(True, "rejects invalid symptom severity")

        print("\nSync:")
        # Same date twice in one request: the backend keeps the last entry
        dup_day = next(d for d in days if d["date"] == (today - timedelta(days=10)).isoformat())
        stale = {**dup_day, "resting_hr_bpm": 99.9}
        request = HealthSyncRequest(timezone=args.timezone, days=[stale, *days], events=events)
        first = service.sync(db, username, request)
        check(first.days_saved == len(days), f"first sync saved {first.days_saved} days", f"expected {len(days)}")
        check(first.events_added == len(events), f"first sync added {first.events_added} HealthKit events")
        stored = db.execute(
            select(DailyHealthMetrics.resting_hr_bpm).where(
                DailyHealthMetrics.username == username, DailyHealthMetrics.date == date.fromisoformat(dup_day["date"])
            )
        ).scalar_one()
        check(stored == dup_day["resting_hr_bpm"], "duplicate date in one request: last entry wins", f"got {stored}")

        again = service.sync(db, username, HealthSyncRequest(timezone=args.timezone, days=days, events=events))
        check(
            again.days_saved == len(days) and again.events_added == 0 and again.events_skipped == len(events),
            "re-sync is idempotent (days upserted, events skipped)",
            str(again),
        )

        n_logs = seed_symptom_logs(db, username, today, tz)
        print(f"  seeded {n_logs} symptom logs across {len(SYMPTOM_LOGS)} days")

        if HealthTrendsService is None:
            print("\nSkipping trends checks: this backend has no GET /health/trends (wrong branch?).")
            print(f"\n{'All checks passed.' if check.failed == 0 else f'{check.failed} check(s) FAILED.'}")
            sys.exit(1 if check.failed else 0)

        print("\nTrends endpoint data (what the chart's 30-day window receives):")
        start = today - timedelta(days=CHART_DAYS - 1)
        trends = HealthTrendsService().get_trends(db, username, start, today)
        by_ago = {(today - t.date).days: t for t in trends}

        check(len(trends) == CHART_DAYS, f"{CHART_DAYS} consecutive days returned", f"got {len(trends)}")
        check(trends[0].date == start and trends[-1].date == today, "window starts/ends on the right dates")
        check(
            all(by_ago[a].sleep_total_min is None and by_ago[a].hrv_avg_ms is None for a in NO_ROW_DAYS),
            "no-data days come back as null gaps",
        )
        check(by_ago[15].hrv_avg_ms is not None, "isolated reading between gaps is present (day 15)")
        check(
            by_ago[6].sleep_total_min is None and by_ago[6].hrv_avg_ms is not None,
            "partial day: sleep missing, heart data present (day 6)",
        )
        check(by_ago[5].hrv_avg_ms is None and by_ago[5].resting_hr_bpm is not None, "partial day: HRV missing (day 5)")
        check(
            by_ago[0].sleep_total_min is not None and by_ago[0].hrv_avg_ms is None,
            "today: sleep in, HRV/RHR not yet computed",
        )
        check(by_ago[23].symptom_count == 2, "two logs on one day -> symptom_count 2 (day 23)")
        check(by_ago[17].symptom_count == 1 and by_ago[17].sleep_total_min is None, "symptom on a no-data day (day 17)")
        check(by_ago[8].symptom_count == 1, "late-evening log lands on its local day (day 8, 23:40)")
        check(by_ago[9].symptom_count == 0 and by_ago[7].symptom_count == 0, "...and not on the days around it")
        check(sum(t.symptom_count for t in trends) == 9, "out-of-window symptom (day 35) excluded")
        check(
            by_ago[22].sleep_total_min == 205 and by_ago[21].sleep_total_min == 655,
            "extreme but valid sleep values stored (3h25m, 10h55m)",
        )

        flare = [t for a, t in by_ago.items() if a in FLARE_DAYS and t.hrv_avg_ms]
        calm = [t for a, t in by_ago.items() if a not in FLARE_DAYS and a not in PRE_FLARE_DAYS and t.hrv_avg_ms]
        f_hrv = sum(t.hrv_avg_ms for t in flare) / len(flare)
        c_hrv = sum(t.hrv_avg_ms for t in calm) / len(calm)
        check(f_hrv < c_hrv, f"flare days show lower HRV ({f_hrv:.1f} vs {c_hrv:.1f} ms)")

        print("\n  ago  date        sleep   HRV    RHR   symptoms")
        for t in trends:
            sleep = f"{t.sleep_total_min / 60:4.1f}h" if t.sleep_total_min is not None else "   — "
            hrv = f"{t.hrv_avg_ms:5.1f}" if t.hrv_avg_ms is not None else "   — "
            rhr = f"{t.resting_hr_bpm:5.1f}" if t.resting_hr_bpm is not None else "   — "
            sym = "●" * t.symptom_count
            print(f"  {(today - t.date).days:3d}  {t.date}  {sleep}  {hrv}  {rhr}   {sym}")

        print(f"\n{'All checks passed.' if check.failed == 0 else f'{check.failed} check(s) FAILED.'}")
        sys.exit(1 if check.failed else 0)
    finally:
        current_username.reset(ctx)
        db.close()


if __name__ == "__main__":
    main()
