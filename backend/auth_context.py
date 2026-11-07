"""Authorization: request-scoped owner for user-owned rows

get_current_user sets current_username for the request, then session events
hide every other user's rows and stamp new rows with the current user.
With no signed-in user, owned rows are hidden. system_access() opts out.
"""

from contextlib import contextmanager
from contextvars import ContextVar

from sqlalchemy import event, false, inspect
from sqlalchemy.orm import Session, with_loader_criteria

current_username: ContextVar[str | None] = ContextVar("current_username", default=None)
_system_access: ContextVar[bool] = ContextVar("system_access", default=False)

_registered = False


@contextmanager
def system_access():
    """Skip the ownership filter. For trusted code with no signed-in user, such as seeding."""
    token = _system_access.set(True)
    try:
        yield
    finally:
        _system_access.reset(token)


def _owned_models() -> tuple[type, ...]:
    from models.daily_health_metrics import DailyHealthMetrics
    from models.food import Food
    from models.food_log import FoodLog
    from models.healthkit_event import HealthKitEvent
    from models.metrics import Metrics
    from models.symptom import Symptom
    from models.symptom_log import SymptomLog

    return (Food, FoodLog, Symptom, SymptomLog, Metrics, DailyHealthMetrics, HealthKitEvent)


def _no_rows(_cls):
    """Match nothing when no user is signed in."""
    return false()


def _filter_owned_rows(execute_state) -> None:
    """Limit reads and writes to the signed-in user.

    No signed-in user matches no rows. system_access() skips this on purpose.
    """
    if _system_access.get() or not execute_state.is_orm_statement:
        return
    if not (execute_state.is_select or execute_state.is_update or execute_state.is_delete):
        return
    username = current_username.get()
    criteria = _criteria(username) if username is not None else _no_rows
    execute_state.statement = execute_state.statement.options(
        *[
            with_loader_criteria(
                model,
                criteria,
                include_aliases=True,
                propagate_to_loaders=False,
            )
            for model in _owned_models()
        ]
    )


def _criteria(owner: str):
    def restrict(cls):
        return cls.username == owner

    return restrict


def _stamp(instance) -> None:
    username = current_username.get()
    if username is None or not isinstance(instance, _owned_models()):
        return
    instance.username = username


def _stamp_on_attach(session: Session, instance) -> None:
    """Assign the owner when a new object joins the session, not when a row is loaded."""
    if inspect(instance).transient:
        _stamp(instance)


def _assign_owner(session: Session, flush_context, instances) -> None:
    """Stamp new rows with the signed-in user and refuse owner changes."""
    username = current_username.get()
    if username is None:
        return

    for obj in session.new:
        _stamp(obj)
    for obj in session.dirty:
        if not isinstance(obj, _owned_models()):
            continue
        history = inspect(obj).attrs.username.history
        if history.has_changes():
            obj.username = username


def register_ownership_filter() -> None:
    """Attach the ownership events once for every Session."""
    global _registered
    if _registered:
        return
    _registered = True
    event.listen(Session, "do_orm_execute", _filter_owned_rows)
    event.listen(Session, "before_attach", _stamp_on_attach)
    event.listen(Session, "before_flush", _assign_owner)
