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


class AgentDesktopSubprocessAdapter:
    """Optional adapter bridging to Vercel's agent-desktop CLI if installed on the host."""
    name = "agent_desktop_cli"

    def __init__(self, cli_bin: str = "agent-desktop"):
        self.cli_bin = shutil.which(cli_bin) or cli_bin

    def is_available(self) -> bool:
        return shutil.which(self.cli_bin) is not None

    def _run_cli(self, args: list[str]) -> dict:
        cmd = [self.cli_bin] + args + ["--json"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                try:
                    return json.loads(res.stdout)
                except Exception:
                    return {"ok": True, "raw": res.stdout}
            return {"ok": False, "error": res.stderr or res.stdout}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    async def observe(self, route: int = 2, root_ref: str | None = None) -> Screen:
        data = self._run_cli(["snapshot"])
        # Format into Screen schema
        scr = Screen(
            platform="windows",
            app=data.get("app", ""),
            window_title=data.get("title", ""),
            elements=[],
            snapshot_id=data.get("snapshot_id", ""),
        )
        scr.ensure_snapshot_id()
        return scr

    async def apply(self, step: Step, screen: Screen | None = None) -> ActionResult:
        a = step.action
        cmd = ["action", a.type]
        if hasattr(a, "mark") and a.mark:
            cmd.extend(["--mark", str(a.mark)])
        if hasattr(a, "ref") and a.ref:
            cmd.extend(["--ref", str(a.ref)])
        res = self._run_cli(cmd)
        if res.get("ok"):
            return ActionResult.success(a.type, data=res, detail=str(res))
        return ActionResult.failure(a.type, ActionErrorCode.ACTION_FAILED, detail=str(res.get("error", "CLI failure")))

    def list_windows(self) -> list[WindowInfo]:
        res = self._run_cli(["windows", "list"])
        windows = res.get("data", {}).get("windows", [])
        return [
            WindowInfo(hwnd=w.get("id", 0), title=w.get("title", ""), class_name=w.get("app", ""))
            for w in windows
        ]

    def get_capabilities(self) -> dict:
        return {
            "adapter": self.name,
            "platform": "external_cli",
            "available": self.is_available(),
            "binary": self.cli_bin,
            "routes": [2],
            "semantic_input": True,
            "physical_input": False,
            "window_management": True,
        }

