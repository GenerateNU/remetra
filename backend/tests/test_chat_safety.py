"""Tests for chatbot/safety.py: the emergency check and trigger check enforced in code."""

import pytest

from chatbot.safety import check_triggers, find_unreported_claims, is_emergency


class TestIsEmergency:
    @pytest.mark.parametrize(
        "text",
        [
            "I can't breathe",
            "I can’t   breathe!!",  # curly apostrophe, extra spaces, punctuation
            "I CANT BREATH",  # caps and misspelling
            "having trouble breathing after lunch",
            "my throat feels like it is closing",
            "Throat swollen",
            "my tongue is swollen",
            "lips swelling",
            "I think this is anaphylaxis",
            "had to use my Epi-Pen",
            "epipen",
            "chest pain after coffee, is that a pattern?",  # emergency wording wins even inside a data question
            "I passed out",
            "I keep fainting",
            "had a seizure",
            "I might overdose",
            "vomiting blood",
            "I want to hurt myself",
            "thinking about suicide",
            "I want to end my life",
        ],
    )
    def test_emergency_wording_detected(self, text):
        assert is_emergency(text)

    @pytest.mark.parametrize(
        "text",
        [
            "How was my week?",
            "Do breathing exercises help bloating?",
            "Is my chest of drawers a trigger?",
            "Which meals did I log on Monday?",
            "",
        ],
    )
    def test_ordinary_questions_not_flagged(self, text):
        assert not is_emergency(text)

    @pytest.mark.parametrize("text", ["I fainted from boredom lol", "throat swelling went away last week"])
    def test_errs_on_the_side_of_flagging(self, text):
        """Jokes and past events still get the safety reply: over-flagging is safer than missing one."""
        assert is_emergency(text)

    @pytest.mark.parametrize(
        "text",
        [
            "pain in my chest",
            "pressure in the chest",
            "my lips swelled up",
            "my face is puffing up",
            "swelling in my throat",
            "severe allergic reaction",
            "I think I'm having an allergic reaction",
            "I want to unalive myself",
        ],
    )
    def test_previously_missed_phrasings(self, text):
        assert is_emergency(text)

    @pytest.mark.parametrize(
        "text",
        [
            "I had a mild allergic reaction to pollen as a kid, does that matter?",
            "my face looks tired in photos",
            "my chest is fine but my stomach hurts",
        ],
    )
    def test_new_patterns_stay_narrow(self, text):
        assert not is_emergency(text)


class TestCheckTriggers:
    def test_no_claims_always_allowed(self):
        assert check_triggers([], [])
        assert check_triggers([], ["gluten"])

    def test_reported_trigger_allowed_ignoring_case_and_spaces(self):
        assert check_triggers(["  Gluten "], ["gluten"])
        assert check_triggers(["gluten"], [" GLUTEN"])

    def test_unreported_trigger_refused(self):
        assert not check_triggers(["dairy"], ["gluten"])

    def test_one_bad_claim_refuses_the_whole_answer(self):
        assert not check_triggers(["gluten", "dairy"], ["gluten"])

    def test_empty_report_refuses_any_claim(self):
        assert not check_triggers(["gluten"], [])

    def test_partial_name_is_not_a_match(self):
        assert not check_triggers(["glute"], ["gluten"])
        assert not check_triggers(["gluten free bread"], ["gluten"])


class TestFindUnreportedClaims:
    @pytest.mark.parametrize(
        "answer",
        [
            "Gluten is definitely your trigger.",
            "Looks like dairy is causing your bloating!",
            "Honestly? Cut the onions out for a week.",
            "You should avoid garlic.",
            "You seem sensitive to tomatoes.",
            "Your flares line up with coffee.",
            "Your logs look great. But eggs are the culprit here.",
            # a hedge only excuses its own clause, not the claim after it
            "Your logs don't show that yet, but gluten is clearly causing the bloating.",
            "I can't say for sure, but you should probably avoid dairy.",
            "Not enough data, though onion seems to be triggering your symptoms.",
        ],
    )
    def test_claim_in_text_is_caught(self, answer):
        assert find_unreported_claims(answer, allowed=[], vocabulary=[])

    def test_users_own_food_names_are_checked(self):
        answer = "Grandma's lasagna is triggering your headaches."
        assert find_unreported_claims(answer, [], vocabulary=["Grandma's lasagna"]) == ["grandmas lasagna"]
        assert find_unreported_claims(answer, [], vocabulary=[]) == []

    def test_reported_trigger_is_allowed(self):
        assert find_unreported_claims("Gluten is one of your reported triggers.", ["Gluten"], []) == []

    def test_reported_trigger_does_not_cover_another_food(self):
        answer = "Gluten is a reported trigger, and dairy is causing problems too."
        assert find_unreported_claims(answer, ["gluten"], []) == ["dairy"]

    @pytest.mark.parametrize(
        "answer",
        [
            "Your logs don't show gluten as a trigger yet.",
            "I can't say whether dairy is a trigger for you.",
            "There's not enough data to call coffee a trigger.",
            "It's too early to tell if onions cause anything.",
            "Keep logging so we can spot your triggers.",  # trigger wording, but no food named
            "You ate pasta with cheese three times this week.",  # food named, but no claim
            "",
        ],
    )
    def test_non_claims_pass(self, answer):
        assert find_unreported_claims(answer, allowed=[], vocabulary=["pasta"]) == []

    def test_blank_vocabulary_entries_ignored(self):
        assert find_unreported_claims("Avoid stress.", [], vocabulary=["", "  ", None]) == []
