"""A fake Gemini client for chatbot tests. No network calls.

Patch it in with monkeypatch so ChatService() gets it instead of genai.Client:
    monkeypatch.setattr("services.chat_service.genai.Client", lambda **_: fake)
"""

import json
from types import SimpleNamespace
from typing import Callable, Optional, Union

Reply = Union[str, dict]


class FakeGeminiClient:
    """Mimics client.models.generate_content and records every call.

    reply: what the "model" returns. A dict is sent as JSON, a str is sent as-is (for broken output),
        and a callable gets the contents string and returns either, to simulate a model that reacts
        to what it reads (e.g. one that obeys instructions hidden in a note).
    error: raised instead of replying, to simulate an API failure.
    """

    def __init__(self, reply: Union[Reply, Callable[[str], Reply], None] = None, error: Optional[Exception] = None):
        self.reply = (
            reply if reply is not None else {"answer": "You logged 2 meals this week.", "triggers_mentioned": []}
        )
        self.error = error
        self.calls: list[dict] = []
        self.models = self

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        if self.error:
            raise self.error
        reply = self.reply(kwargs["contents"]) if callable(self.reply) else self.reply
        return SimpleNamespace(text=reply if isinstance(reply, str) else json.dumps(reply))

    @property
    def last_contents(self) -> str:
        return self.calls[-1]["contents"]

    @property
    def last_system_prompt(self) -> str:
        return self.calls[-1]["config"]["system_instruction"]


def gullible_model(contents: str) -> dict:
    """A model that falls for prompt injection: if anything it reads says a food is a trigger, it repeats it."""
    lowered = contents.lower()
    if "gluten is my trigger" in lowered or "gluten is a trigger" in lowered:
        return {"answer": "Gluten is definitely your trigger. Cut it out completely!", "triggers_mentioned": ["gluten"]}
    return {"answer": "Your logs don't show a trigger yet.", "triggers_mentioned": []}
