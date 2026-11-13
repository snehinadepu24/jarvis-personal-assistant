from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any, Protocol

from jarvis.actions.base import ActionResult
from jarvis.core.schema import ActionErrorCode, Screen, Step


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    class_name: str
    pid: int = 0
    is_active: bool = False
    is_minimized: bool = False
    is_maximized: bool = False
    rect: tuple[int, int, int, int] = (0, 0, 0, 0)


class DesktopAdapter(Protocol):
    name: str

    async def observe(self, route: int = 2, root_ref: str | None = None) -> Screen:
        ...

    async def apply(self, step: Step, screen: Screen | None = None) -> ActionResult:
        ...

    def list_windows(self) -> list[WindowInfo]:
        ...

    def get_capabilities(self) -> dict:
        ...


class MockDesktopAdapter:
    name = "mock_adapter"

    def __init__(self, backend, executor):
        self.backend = backend
        self.executor = executor

    async def observe(self, route: int = 2, root_ref: str | None = None) -> Screen:
        scr = self.backend.observe(route=route)
        scr.ensure_snapshot_id()
        return scr

    async def apply(self, step: Step, screen: Screen | None = None) -> ActionResult:
        return await self.executor.apply(step, screen=screen)

    def list_windows(self) -> list[WindowInfo]:
        raw = self.backend.list_windows()
        return [
            WindowInfo(
                hwnd=w.get("wid", 0),
                title=w.get("title", ""),
                class_name=w.get("cls", ""),
                is_active=(w.get("key") == getattr(self.backend, "active_wid", "")),
            )
            for w in raw
        ]

    def get_capabilities(self) -> dict:
        return {
            "adapter": self.name,
            "platform": "simulated",
            "routes": [1, 2, 3, 4],
            "semantic_input": True,
            "physical_input": False,
            "window_management": True,
        }


class UiaDesktopAdapter:
    name = "uia_adapter"

    def __init__(self, backend, executor):
        self.backend = backend
        self.executor = executor

    async def observe(self, route: int = 2, root_ref: str | None = None) -> Screen:
        scr = await self.backend.observe(route=route)
        scr.ensure_snapshot_id()
        return scr

    async def apply(self, step: Step, screen: Screen | None = None) -> ActionResult:
        return await self.executor.apply(step, screen=screen)

    def list_windows(self) -> list[WindowInfo]:
        raw = self.backend.list_windows()
        return [
            WindowInfo(
                hwnd=w.get("wid", 0),
                title=w.get("title", ""),
                class_name=w.get("cls", ""),
            )
            for w in raw
        ]

    def get_capabilities(self) -> dict:
        return {
            "adapter": self.name,
            "platform": "windows_native",
            "routes": [1, 2, 3, 4],
            "semantic_input": True,
            "physical_input": True,
            "window_management": True,
        }

