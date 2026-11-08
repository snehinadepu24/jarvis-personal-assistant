from __future__ import annotations

import asyncio
from pathlib import Path

from jarvis.bench.runner import TaskSpec, run_benchmark, run_spec
from jarvis.config import Config
from jarvis.core.skills_format import SkillModel

TASKS = Path(__file__).resolve().parent.parent / "jarvis" / "bench" / "tasks"


def cfg(tmp_path) -> Config:
    c = Config.load()
    c.data_dir = tmp_path
    c.backend = "mock"
    return c


def test_record_and_replay_skill_zero_llm(tmp_path):
    spec = TaskSpec.load(TASKS / "bluetooth_toggle.yaml")
    r1 = asyncio.run(run_spec(spec, cfg(tmp_path), planner_mode="scripted", seed=0, record_skill_name="bt_skill"))
    assert r1["status"] == "done" and r1["skill_saved"]
    skill = SkillModel.load(r1["skill_saved"])
    assert skill.name == "bt_skill"
    toggle_step = next(s for s in skill.steps if s.action.get("type") == "toggle")
    assert "mark" not in toggle_step.action
    sel = toggle_step.select
    assert sel.get("automation_id") == "bluetooth-toggle" or sel.get("name_exact") == "Bluetooth"

    r2 = asyncio.run(run_spec(spec, cfg(tmp_path), planner_mode="scripted", seed=1, skill_path=Path(r1["skill_saved"])))
    assert r2["status"] == "done" and r2["checker_ok"]
    assert r2["llm_calls"] == 0


def test_benchmark_arm_d_skills_warm(tmp_path):
    results = asyncio.run(run_benchmark(cfg(tmp_path), [TASKS / "teams_draft.yaml"], planner_mode="scripted", arms=["D"], seeds=3))
    r = results[0]
    assert r["checker_success"] == 1.0
    assert r["llm_calls_avg"] == 0
    assert r["replay_determinism"] is True


def test_replay_refuses_tier3(tmp_path):
    from jarvis.agent.skills import record_skill, replay_skill
    from jarvis.connectors.files import FilesConnector
    from jarvis.actions.mock_executor import MockExecutor
    from jarvis.perception.mock_backend import SimulatedDesktop

    desktop = SimulatedDesktop(fs_root=tmp_path)
    desktop.open_app("Microsoft Teams")
    screen = desktop.observe()
    send_el = next(e for e in screen.elements if e.automation_id == "send-btn")
    trace = [{"action": {"type": "click", "mark": send_el.mark}, "select": {"automation_id": "send-btn"}, "expect": "sent"}]
    skill = record_skill("sendy", trace)
    ok, detail = asyncio.run(replay_skill(skill, screen, MockExecutor(desktop, FilesConnector(tmp_path))))
    assert not ok and "tier 3" in detail
    assert desktop.teams_send_invoked is False
