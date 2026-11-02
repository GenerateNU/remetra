"""Turning timestamps into a user's local calendar day.

Logs are stored as UTC instants, but people think in days on their own clock: a 23:30 dinner
belongs to that evening, not to the next UTC day. Everything that groups logs by day goes
through here so the answer is the same everywhere.

The timezone is always passed in by the caller, never guessed here. The calendar uses the
timezone the device sends with each request, because that is the clock the user is looking at
and the one the app's day list groups by. Health trends can pass the timezone of the latest
health sync instead; either way the grouping itself is shared.
"""

from datetime import date, datetime, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import Date, cast, func
from sqlalchemy.sql.elements import ColumnElement


def parse_timezone(name: str) -> ZoneInfo:
    """IANA timezone by name, e.g. "America/New_York". Raises ValueError for anything else."""
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, OSError) as e:
        raise ValueError(f"Unknown timezone: {name!r}") from e


def local_date_column(timestamp_column, timezone: str) -> ColumnElement[date]:
    """SQL expression for the local date of a timestamptz column, so Postgres does the grouping.

    `timezone(name, timestamptz)` is Postgres' AT TIME ZONE: it gives the wall-clock time in
    that zone, and casting that to a date gives the local day.
    """
    return cast(func.timezone(timezone, timestamp_column), Date)


def to_local_date(timestamp: datetime, tz: tzinfo) -> date:
    """Python equivalent of local_date_column, for timestamps already loaded into memory."""
    return timestamp.astimezone(tz).date()
