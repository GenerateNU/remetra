"""Turns a user's stored family confidences into weekly labels (docs/model-v2-draft.md, Labels). Read only."""

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from analysis.weekly_labels import (
    EXPOSURE_SETTLE_HOURS,
    Label,
    MergeGroup,
    combine,
    is_no_clear_pattern,
    label_for,
    load_merge_groups,
    meal_exposures,
    meaningful_components,
    to_probability,
)
from repositories.family_confidence_repository import FamilyConfidenceRepository
from repositories.weekly_results_repository import WeeklyResultsRepository
from schemas.weekly_results import WeeklyLabelItem, WeeklyResultsResponse


@dataclass(frozen=True)
class _Unit:
    """What gets one label: a single component, or an always-together group."""

    id: str
    display_name: str
    members: tuple[str, ...]
    is_group: bool


class WeeklyResultsService:
    def __init__(self):
        self.confidence_repo = FamilyConfidenceRepository()
        self.repo = WeeklyResultsRepository()

    def get_weekly_results(self, db: Session, username: str, now: datetime | None = None) -> WeeklyResultsResponse:
        """Label every component (or merge group) the user has eaten at a meaningful amount.

        Uses Q_c = 1 - prod_f(1 - q_{c,f}) per component and Q_G = 1 - prod_{c in G}(1 - Q_c) per group.
        """
        now = now or datetime.now(timezone.utc)
        rows = self.confidence_repo.get_all_confidences(db, username)
        if not rows:
            return WeeklyResultsResponse()

        family_qs: dict[str, list[float]] = defaultdict(list)
        display_names: dict[str, str] = {}
        for row in rows:
            family_qs[row.component.slug].append(to_probability(row.log_odds))
            display_names[row.component.slug] = row.component.display_name
        component_q = {slug: combine(qs) for slug, qs in family_qs.items()}

        meals = self._settled_meals(db, username, now)

        units = _units(display_names, load_merge_groups())
        response = WeeklyResultsResponse(
            groups_total=len(units), first_meal_at=self.repo.get_first_meal_time(db, username)
        )
        labelled: list[tuple[float, Label]] = []
        for unit in units:
            exposure_count = sum(1 for meal in meals if meal.intersection(unit.members))
            if exposure_count == 0:
                continue
            confidence = combine(component_q[slug] for slug in unit.members)
            label = label_for(confidence, exposure_count, self._recheck_completed(db, username, unit.id))
            labelled.append((confidence, label))
            getattr(response, label.value).append(
                WeeklyLabelItem(
                    id=unit.id,
                    display_name=unit.display_name,
                    is_group=unit.is_group,
                    member_slugs=list(unit.members),
                    label=label,
                )
            )

        for items in (response.likely_trigger, response.still_learning, response.looks_fine):
            items.sort(key=lambda item: item.display_name.lower())
        response.no_clear_pattern = is_no_clear_pattern(labelled)
        response.groups_checked = len(response.likely_trigger) + len(response.looks_fine)
        return response

    def _settled_meals(self, db: Session, username: str, now: datetime) -> list[set[str]]:
        """For each meal whose 48 h window has passed, the components it contained at a meaningful amount."""
        levels = self.repo.get_ingredient_levels(db)
        cutoff = now - timedelta(hours=EXPOSURE_SETTLE_HOURS)
        return [
            meaningful_components(meal_exposures(ingredients, levels))
            for ingredients in self.repo.get_meal_ingredients(db, username, cutoff)
        ]

    def _recheck_completed(self, db: Session, username: str, unit_id: str) -> bool:
        """Stub: re-checks aren't recorded yet, so every high-confidence food is treated as re-checked.

        TODO: return whether the user completed a re-check of this component or group once that is tracked.
        """
        return True


def _units(display_names: dict[str, str], merge_groups: tuple[MergeGroup, ...]) -> list[_Unit]:
    """One unit per merge group with any member present, plus one per component that is in no group."""
    units = []
    grouped: set[str] = set()
    for group in merge_groups:
        members = tuple(slug for slug in group.members if slug in display_names)
        if members:
            units.append(_Unit(group.id, group.display_name, members, is_group=True))
            grouped.update(members)
    for slug, name in display_names.items():
        if slug not in grouped:
            units.append(_Unit(slug, name, (slug,), is_group=False))
    return units
