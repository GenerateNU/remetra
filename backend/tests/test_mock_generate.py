"""Generating users: repeatable, balanced types, unique mock_ usernames, and a truth file that matches the data."""

import json
from datetime import date

from scripts.mock_users.generate import generate_users, main, truth_records, write_truth_file
from scripts.mock_users.shapes import USERNAME_PREFIX, load_user_types

END = date(2026, 11, 1)


def test_same_seed_gives_same_users():
    assert generate_users(42, 8, END) == generate_users(42, 8, END)


def test_different_seeds_give_different_users():
    assert generate_users(1, 4, END) != generate_users(2, 4, END)


def test_zero_users_gives_empty_list():
    assert generate_users(42, 0, END) == []


def test_usernames_are_unique_and_start_with_mock():
    users = generate_users(42, 12, END)
    names = [u.username for u in users]

    assert all(name.startswith(USERNAME_PREFIX) for name in names)
    assert len(set(names)) == len(names)


def test_types_are_balanced():
    types, _ = load_user_types()
    users = generate_users(42, len(types) * 3, END)

    for name in types:
        assert sum(u.user_type.name == name for u in users) == 3


def test_users_differ_from_each_other():
    users = generate_users(42, 2, END)

    assert users[0].meals != users[1].meals


def test_truth_records_match_generated_data():
    users = generate_users(42, 8, END)

    for user, record in zip(users, truth_records(users)):
        assert record["username"] == user.username
        assert record["user_type"] == user.user_type.name
        assert record["planted_reactions"] == sum(s.planted for s in user.symptoms)
        if user.user_type.trigger:
            assert record["trigger"]["component"] == user.user_type.trigger.component
        else:
            assert record["trigger"] is None
            assert record["planted_reactions"] == 0


def test_write_truth_file(tmp_path):
    users = generate_users(42, 4, END)
    path = tmp_path / "nested" / "truth.json"

    write_truth_file(users, path, seed=42, end_date=END, days=60)
    truth = json.loads(path.read_text())

    assert truth["seed"] == 42
    assert truth["end_date"] == "2026-11-01"
    assert [r["username"] for r in truth["users"]] == [u.username for u in users]


def test_main_writes_truth_file(tmp_path, capsys):
    path = tmp_path / "truth.json"

    main(["--count", "4", "--seed", "1", "--days", "10", "--truth", str(path)])

    assert len(json.loads(path.read_text())["users"]) == 4
    assert "Wrote truth file for 4 users" in capsys.readouterr().out
