from __future__ import annotations

from typing import Any
from jarvis.actions.base import ActionResult
from jarvis.core.schema import Screen, Step
from jarvis.desktop.adapter import DesktopAdapter


class DesktopSpecialistAgent:
    """Specialist Agent: Controls desktop surfaces, window management, and UIA/OCR perception."""

    def __init__(self, adapter: DesktopAdapter):
        self.adapter = adapter
        self.current_screen: Screen | None = None

    async def observe_surface(self, route: int = 2, root_ref: str | None = None) -> Screen:
        self.current_screen = await self.adapter.observe(route=route, root_ref=root_ref)
        return self.current_screen

    async def execute_action(self, step: Step) -> ActionResult:
        return await self.adapter.apply(step, screen=self.current_screen)

    def list_open_windows(self) -> list[dict]:
        windows = self.adapter.list_windows()
        return [{"hwnd": w.hwnd, "title": w.title, "class": w.class_name} for w in windows]

