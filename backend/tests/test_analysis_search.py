"""Unit tests for backend analysis binary-search helpers."""

from datetime import datetime

import pytest

from analysis.models import FoodLogEntry, SymptomLogEntry
from analysis.search import get_food_logs_within_time_window_before_symptoms


def food_at(name: str, iso_time: str) -> FoodLogEntry:
    return FoodLogEntry(
        timestamp=datetime.fromisoformat(iso_time),
        ingredients=[name],
    )


def symptom_at(name: str, iso_time: str) -> SymptomLogEntry:
    return SymptomLogEntry(
        timestamp=datetime.fromisoformat(iso_time),
        symptom_name=name,
        location="head",
        sensation="ache",
        intensity=6,
        duration=30,
    )


class TestBinarySearchWindow:
    def test_returns_foods_in_window_before_symptom(self):
        foods = [
            food_at("toast", "2026-03-16T08:00:00+00:00"),
            food_at("coffee", "2026-03-16T09:15:00+00:00"),
            food_at("eggs", "2026-03-16T10:30:00+00:00"),
        ]
        symptoms = [symptom_at("headache", "2026-03-16T11:00:00+00:00")]

        result = get_food_logs_within_time_window_before_symptoms(foods, symptoms, 2)

        assert len(result) == 1
        assert [f.ingredients[0] for f in result[0].food_logs] == ["coffee", "eggs"]

    def test_includes_window_start_excludes_symptom_timestamp(self):
        foods = [
            food_at("start-boundary", "2026-03-16T09:00:00+00:00"),
            food_at("exact-symptom-time", "2026-03-16T11:00:00+00:00"),
        ]
        symptoms = [symptom_at("nausea", "2026-03-16T11:00:00+00:00")]

        result = get_food_logs_within_time_window_before_symptoms(foods, symptoms, 2)

        assert [f.ingredients[0] for f in result[0].food_logs] == ["start-boundary"]

    def test_handles_unsorted_food_logs(self):
        foods = [
            food_at("latest", "2026-03-16T10:45:00+00:00"),
            food_at("earliest", "2026-03-16T08:20:00+00:00"),
            food_at("middle", "2026-03-16T09:10:00+00:00"),
        ]
        symptoms = [symptom_at("rash", "2026-03-16T11:00:00+00:00")]

        result = get_food_logs_within_time_window_before_symptoms(foods, symptoms, 2)

        assert [f.ingredients[0] for f in result[0].food_logs] == ["middle", "latest"]

    def test_raises_for_negative_time_window(self):
        foods = [food_at("toast", "2026-03-16T08:00:00+00:00")]
        symptoms = [symptom_at("headache", "2026-03-16T11:00:00+00:00")]

        with pytest.raises(ValueError, match="time_window_hours must be >= 0"):
            get_food_logs_within_time_window_before_symptoms(foods, symptoms, -1)
