from __future__ import annotations

import os

import pytest

from jarvis.llm.base import LLMError, Usage, extract_json
from jarvis.llm.costs import COSTS


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_fenced():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_prose():
    assert extract_json('Sure! {"a": {"b": 2}} done') == {"a": {"b": 2}}


def test_extract_json_invalid():
    with pytest.raises(LLMError):
        extract_json("no json here")


def test_pricing():
    usd = COSTS.usd("gemini-3.6-flash", 1_000_000, 1_000_000)
    assert usd == pytest.approx(9.0)
    assert COSTS.usd("unknown-model", 1000, 1000) == 0.0


def test_usage_add():
    u = Usage(model="m", input_tokens=10, output_tokens=5, usd=0.1)
    u.add(Usage(model="m", input_tokens=1, output_tokens=1, usd=0.2))
    assert u.input_tokens == 11 and u.usd == pytest.approx(0.3)


@pytest.mark.live
def test_gemini_live_step_planning():
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        pytest.skip("GEMINI_API_KEY not set")
    import asyncio

    from jarvis.llm.gemini import GeminiLLM
    from jarvis.llm.router import LlmRouter
    from jarvis.perception.mock_backend import SimulatedDesktop

    async def run():
        desktop = SimulatedDesktop()
        desktop.open_app("Settings")
        router = LlmRouter(GeminiLLM(), thinking="low")
        router.set_goal("Turn Bluetooth off in Windows Settings")
        screen = desktop.observe()
        step, usage = await router.plan(
            "Turn Bluetooth off in Windows Settings", "", 1, 25,
            "(task start)", "-", screen, "(no changes)", "WINDOW title='Settings' route=2 confidence=0.90", 2,
        )
        return step, usage

    step, usage = asyncio.run(run())
    assert step.action.type in ("open_url", "toggle", "click", "focus_window", "open_app")
    assert usage.usd >= 0.0
