from __future__ import annotations

from dataclasses import dataclass, field

from typing import Optional

from jarvis.core.schema import Rect, Screen, Step
from jarvis.core.skills_format import SkillModel, SkillStep, resolve_element
from jarvis.safety.risk import classify


class ScriptError(RuntimeError):
    pass


@dataclass
class ScriptEntry:
    thought: str
    action: dict
    expect: str
    select: dict = field(default_factory=dict)


class ScriptedPlanner:
    name = "scripted"

    def __init__(self, entries: list[ScriptEntry]):
        self.entries = entries
        self._i = 0

    async def intent(self, goal: str) -> dict:
        return {"verb": "scripted", "goal": goal}

    async def plan(self, goal, progress, step_no, max_steps, last_action, last_result, screen: Screen, diff_line, window_line, route, screenshot: Optional[bytes] = None) -> tuple[Step, Usage]:
        if self._i >= len(self.entries):
            raise ScriptError("script exhausted; task did not reach done")
        e = self.entries[self._i]
        self._i += 1
        action = dict(e.action)
        if "mark" in action:
            el = screen.by_mark(action["mark"])
            if el is None:
                raise ScriptError(f"script mark {action['mark']} not on screen")
        elif e.select:
            el = resolve_element(screen, e.select)
            if el is None:
                raise ScriptError(f"script target {e.select} not on screen")
            action["mark"] = el.mark
        step = Step(thought=e.thought, action=action, expect=e.expect)
        return step, Usage(model=self.name)

    def finished(self) -> bool:
        return self._i >= len(self.entries)


from jarvis.llm.base import Usage  # noqa: E402


def record_skill(name: str, trace: list[dict]) -> SkillModel:
    steps = []
    for t in trace:
        action = dict(t["action"])
        sel = t.get("select") or t.get("selector") or {}
        if sel and "mark" in action:
            action.pop("mark", None)
        steps.append(SkillStep(select=sel, action=action, postcondition=t.get("expect", "")))
    return SkillModel(name=name, steps=steps)


def planner_from_skill(skill: SkillModel) -> "ScriptedPlanner":
    entries = [
        ScriptEntry(thought=f"skill replay {skill.name}", action=s.action, expect=s.postcondition, select=s.select)
        for s in skill.steps
    ]
    return ScriptedPlanner(entries)


async def replay_skill(skill: SkillModel, screen: Screen, executor) -> tuple[bool, str]:
    for s in skill.steps:
        el = resolve_element(screen, s.select)
        if el is None:
            return False, f"selector {s.select} unresolved; hand off to LLM"
        step = Step(thought=f"skill replay: {skill.name}", action={**s.action, "mark": el.mark}, expect=s.postcondition)
        risk = classify(step, screen)
        if risk.tier >= 3:
            return False, f"skill step {s.action.get('type')} is tier {risk.tier}; hand off to LLM"
        result = await executor.apply(step)
        if not result.ok:
            return False, f"step failed: {result.detail}"
    return True, "skill replay complete"
