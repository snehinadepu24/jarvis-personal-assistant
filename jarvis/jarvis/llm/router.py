from __future__ import annotations

import json
import re

from jarvis.core.prompts import build_step_message, system_prompt
from jarvis.core.schema import Step, step_schema
from jarvis.llm.base import LLMError, Usage


class HeuristicIntent:
    name = "heuristic-intent"

    VERBS = {
        "open": "open", "launch": "open", "start": "open", "go to": "open",
        "toggle": "toggle", "turn on": "toggle", "turn off": "toggle", "enable": "toggle", "disable": "toggle",
        "type": "type", "write": "type", "enter": "type",
        "save": "save", "find": "find", "search": "find",
        "draft": "draft", "compose": "draft",
        "rename": "rename", "delete": "delete", "send": "send",
    }

    async def intent(self, goal: str) -> dict:
        g = goal.lower()
        verb = next((v for k, v in sorted(self.VERBS.items(), key=lambda kv: -len(kv[0])) if k in g), "unknown")
        return {"verb": verb, "goal": goal}


class PlanError(RuntimeError):
    def __init__(self, msg: str, marker: str = "plan"):
        super().__init__(msg)
        self.marker = marker


class LlmRouter:
    def __init__(self, planner, small=None, thinking: str = "low", tools_description: str = ""):
        self.planner = planner
        self.small = small or HeuristicIntent()
        self.thinking = thinking
        self.tools_description = tools_description
        self._system = system_prompt("", self.tools_description, json.dumps(step_schema()))

    def set_goal(self, goal: str) -> None:
        self._system = system_prompt(goal, self.tools_description, json.dumps(step_schema()))

    async def intent(self, goal: str) -> dict:
        return await self.small.intent(goal)

    async def plan(
        self, goal, progress, step_no, max_steps, last_action, last_result,
        screen, diff_line, window_line, route, screenshot=None
    ) -> tuple[Step, Usage]:
        from jarvis.perception.serialize import serialize_screen

        msg = build_step_message(
            goal, progress, step_no, max_steps, last_action, last_result,
            screen_block=serialize_screen(screen), diff_line=diff_line, window_line_str=window_line,
            tools=self.tools_description,
        )
        data, usage = await self.planner.complete_json(
            self._system,
            [{"role": "user", "content": msg, "image_bytes": screenshot}],
            step_schema(),
            thinking=self.thinking,
        )
        if data.get("action", {}).get("type") in {
            "click", "double_click", "right_click", "type", "clear",
            "select_item", "toggle", "expand", "collapse",
        }:
            mark = data["action"].get("mark")
            if mark is not None and screen.by_mark(mark) is None:
                raise PlanError(
                    f"planner selected mark [{mark}], but that mark is not present in the live UIA snapshot",
                    marker="invalid_mark",
                )
        if isinstance(data.get('thought'), str) and len(data['thought']) > 1900:
            data['thought'] = data['thought'][:1900]
        if isinstance(data.get('expect'), str) and len(data['expect']) > 900:
            data['expect'] = data['expect'][:900]
        try:
            step = Step(**data)
        except Exception as e:
            raise PlanError(f"planner reply failed validation: {e}", marker="invalid_step") from e
        element_types = {"click", "double_click", "right_click", "type", "clear", "select_item", "toggle", "expand", "collapse", "scroll"}
        if step.action.type in element_types and getattr(step.action, "mark", None) is not None:
            if screen.by_mark(step.action.mark) is None:
                raise PlanError(f"mark [{step.action.mark}] is not on the current screen", marker="invalid_mark")
        return step, usage


def sanitize_screen_for_llm(screen) -> str:
    from jarvis.perception.serialize import serialize_screen

    return serialize_screen(screen)
