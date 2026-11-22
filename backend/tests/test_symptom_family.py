"""Unit tests for mapping symptoms to symptom families."""

import pytest

from models.symptom_family import SymptomFamily, family_for_symptom


@pytest.mark.parametrize(
    ("location", "sensation", "expected"),
    [
        ("Abdomen", "Cramping", SymptomFamily.GI),
        ("Abdomen", "Pain", SymptomFamily.GI),
        ("Whole Body", "Bloating", SymptomFamily.GI),
        ("Throat", "Burning", SymptomFamily.GI),
        ("Skin", "Burning", SymptomFamily.SKIN),
        ("Hands / Fingers", "Itching", SymptomFamily.SKIN),
        ("Head", "Throbbing", SymptomFamily.HEAD),
        ("Eyes", "Sensitivity", SymptomFamily.HEAD),
        ("Eyes", "Itching", None),
        ("Knees", "Stiffness", None),
        ("Lower Back", "Aching", None),
        ("Throat", "Soreness", None),
    ],
)
def test_family_for_symptom(location, sensation, expected):
    assert family_for_symptom(location, sensation) == expected


def test_family_for_symptom_ignores_case_and_whitespace():
    assert family_for_symptom("  abdomen ", "CRAMPING") == SymptomFamily.GI


def test_family_for_symptom_handles_missing_values():
    assert family_for_symptom(None, None) is None
    assert family_for_symptom("", "") is None
