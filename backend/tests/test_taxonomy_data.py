"""Fails CI if the taxonomy files break any rule in scripts/validate_taxonomy.py."""

from scripts.validate_taxonomy import run_checks


def test_taxonomy_files_pass_validation():
    errors, _warnings = run_checks()
    assert errors == [], "\n".join(errors)
