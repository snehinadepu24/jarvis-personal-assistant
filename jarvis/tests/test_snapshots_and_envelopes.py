import asyncio
import pytest
from jarvis.actions.base import ActionResult
from jarvis.actions.mock_executor import MockExecutor
from jarvis.core.schema import (
    ActionErrorCode,
    Click,
    Done,
    Rect,
    Screen,
    Step,
    UiElement,
)
from jarvis.perception.mock_backend import SimulatedDesktop


def test_screen_snapshot_id_and_refs():
    screen = Screen(
        app="Notepad",
        window_title="Untitled - Notepad",
        elements=[
            UiElement(
                mark=1,
                role="edit",
                name="Text Editor",
                control_type=50004,
                rect=Rect(l=0, t=0, r=100, b=100),
                enabled=True,
                key="edit_1",
            ),
            UiElement(
                mark=2,
                role="button",
                name="Close",
                control_type=50000,
                rect=Rect(l=90, t=0, r=100, b=10),
                enabled=True,
                key="btn_close",
            ),
        ],
    )
    sid = screen.ensure_snapshot_id()
    assert sid.startswith("s_")
    assert screen.elements[0].ref == f"@{sid}:e1"
    assert screen.elements[1].ref == f"@{sid}:e2"

    el = screen.by_ref(f"@{sid}:e1")
    assert el is not None
    assert el.name == "Text Editor"


def test_action_result_standard_envelopes():
    res_ok = ActionResult.success("click", detail="Clicked button", input_mode="semantic")
    assert res_ok.ok is True
    assert res_ok.envelope is not None
    assert res_ok.envelope.version == "1.0"
    assert res_ok.envelope.ok is True
    assert res_ok.envelope.command == "click"
    assert res_ok.envelope.error is None
    assert res_ok.input_mode == "semantic"

    res_fail = ActionResult.failure(
        "type",
        ActionErrorCode.NOT_FOUND,
        detail="Element not found",
        suggestion="Take a fresh observation",
        retry=True,
        requires_observe=True,
    )
    assert res_fail.ok is False
    assert res_fail.envelope is not None
    assert res_fail.envelope.ok is False
    assert res_fail.envelope.error.code == ActionErrorCode.NOT_FOUND
    assert res_fail.envelope.error.disposition.retry is True
    assert res_fail.envelope.error.disposition.requires_observe is True
    assert res_fail.envelope.error.suggestion == "Take a fresh observation"


def test_stale_target_rejection():
    desktop = SimulatedDesktop()
    executor = MockExecutor(desktop)
    screen = desktop.observe()
    screen.ensure_snapshot_id()

    # Create step pointing to an obsolete/different snapshot_id
    step_stale = Step(
        thought="Clicking button with stale ref",
        action=Click(type="click", mark=1, snapshot_id="s_old12345", ref="@s_old12345:e1"),
    )

    result = asyncio.run(executor.apply(step_stale, screen=screen))
    assert result.ok is False
    assert result.envelope.error.code == ActionErrorCode.STALE_TARGET
    assert result.envelope.error.disposition.retry is True
    assert result.envelope.error.disposition.requires_observe is True
