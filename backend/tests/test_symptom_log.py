"""
Pydantic validation tests for symptom log schemas.

These tests verify that the SymptomLogCreate schema correctly validates
field constraints (intensity range, duration non-negative).
No database needed for these tests.
"""

from datetime import datetime
from uuid import uuid4

import pytest

from schemas.symptom_log import SymptomLogCreate


def test_create_symptom_log_intensity_too_low():
    """Pydantic should reject intensity < 1."""
    with pytest.raises(ValueError):
        SymptomLogCreate(
            username="testuser",
            symptom_id=uuid4(),
            intensity=0,
            timestamp=datetime(2025, 1, 15, 10, 30),
        )


def test_create_symptom_log_intensity_too_high():
    """Pydantic should reject intensity > 10."""
    with pytest.raises(ValueError):
        SymptomLogCreate(
            username="testuser",
            symptom_id=uuid4(),
            intensity=11,
            timestamp=datetime(2025, 1, 15, 10, 30),
        )


def test_create_symptom_log_negative_duration():
    """Pydantic should reject duration < 0."""
    with pytest.raises(ValueError):
        SymptomLogCreate(
            username="testuser",
            symptom_id=uuid4(),
            intensity=5,
            timestamp=datetime(2025, 1, 15, 10, 30),
            duration=-10,
        )
