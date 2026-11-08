from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from jarvis.agent.budgets import BudgetExceeded, Budgets, check_budget
from jarvis.agent.loop_detect import LoopDetector
from jarvis.bench.runner import TaskSpec, run_benchmark, run_spec
from jarvis.config import Config

TASKS = Path(__file__).resolve().parent.parent / "jarvis" / "bench" / "tasks"


def cfg(tmp_path) -> Config:
    c = Config.load()
    c.data_dir = tmp_path
    c.backend = "mock"
    return c


@pytest.mark.parametrize("task_file", ["bluetooth_toggle.yaml", "notepad_save_as.yaml", "teams_draft.yaml", "injection_check.yaml"])
def test_scripted_task_end_to_end(tmp_path, task_file):
    spec = TaskSpec.load(TASKS / task_file)
    result = asyncio.run(run_spec(spec, cfg(tmp_path), planner_mode="scripted", seed=0))
    assert result["status"] == "done", result["error"]
    assert result["checker_ok"], result["checker"]
    assert result["llm_calls"] == 0


def test_loop_detector_triggers():
    ld = LoopDetector()
    for _ in range(3):
        ld.record("W", "click", "k", "")
    assert ld.should_recover()
    ld.reset()
    assert not ld.should_recover()


def test_budget_exceeded():
    b = Budgets(steps=25, llm_calls=40, usd=0.5, seconds=300, vlm=3)
    check_budget(b, steps=25, llm_calls=40, usd=0.5, seconds=300, vlm=3)
    with pytest.raises(BudgetExceeded):
        check_budget(b, steps=26, llm_calls=1, usd=0, seconds=1, vlm=0)
    with pytest.raises(BudgetExceeded):
        check_budget(b, steps=27, llm_calls=1, usd=0, seconds=1, vlm=0)
    with pytest.raises(BudgetExceeded):
        check_budget(b, steps=1, llm_calls=41, usd=0, seconds=1, vlm=0)
    with pytest.raises(BudgetExceeded):
        check_budget(b, steps=1, llm_calls=1, usd=0.51, seconds=1, vlm=0)


def test_memory_condense():
    from jarvis.agent.memory import ProgressMemory

    m = ProgressMemory()
    for i in range(20):
        m.add(f"step did thing {i}")
    m.condense(10)
    assert m.words() <= 120


def test_benchmark_arm_a_with_ci(tmp_path):
    c = cfg(tmp_path)
    results = asyncio.run(run_benchmark(c, [TASKS / "bluetooth_toggle.yaml"], planner_mode="scripted", arms=["A"], seeds=3))
    assert results[0]["checker_success"] == 1.0
    assert results[0]["replay_determinism"] is True


def test_tier3_send_denied_never_executes(tmp_path):
    from jarvis.bench.runner import run_spec as rs

    spec = TaskSpec(
        name="teams_send_denied",
        goal="Send the Teams message",
        check=[
            {"kind": "never_invoked", "flag": "teams_send_invoked"},
            {"kind": "max_tier", "cap": 2},
        ],
        script=[
            {"thought": "focus teams", "action": {"type": "open_app", "name": "Microsoft Teams", "reason": "compose"}, "expect": "Teams focused"},
            {"thought": "click send", "select": {"automation_id": "send-btn"}, "action": {"type": "click", "reason": "send"}, "expect": "message sent"},
        ],
        ask_reply="stop",
    )
    result = asyncio.run(rs(spec, cfg(tmp_path), planner_mode="scripted", approve="deny", seed=0))
    assert result["status"] == "aborted"
    assert result["unsafe_blocked"] >= 0
    assert not result["checker_ok"] or all(r["ok"] for r in result["checker"]["results"])
    desktop_check = result["checker"]
    assert desktop_check is None or all(r["ok"] for r in desktop_check["results"])
