from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

from jarvis.actions.base import ActionResult
from jarvis.core.schema import ActionErrorCode


@dataclass
class WindowDetail:
    hwnd: int
    title: str
    class_name: str
    is_visible: bool
    is_minimized: bool
    is_maximized: bool
    rect: tuple[int, int, int, int]


class WindowsManagerConnector:
    name = "windows_manager"

    def __init__(self, mock_backend=None):
        self.mock = mock_backend

    def list_windows(self) -> list[WindowDetail]:
        if sys.platform != "win32" or self.mock is not None:
            if self.mock:
                raw = self.mock.list_windows()
                return [
                    WindowDetail(
                        hwnd=w.get("wid", 1000 + i),
                        title=w.get("title", ""),
                        class_name=w.get("cls", ""),
                        is_visible=True,
                        is_minimized=False,
                        is_maximized=False,
                        rect=(0, 0, 1024, 768),
                    )
                    for i, w in enumerate(raw)
                ]
            return []

        import win32gui
        import win32con

        results: list[WindowDetail] = []

        def enum_cb(hwnd, _):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd).strip()
                if title:
                    cls_name = win32gui.GetClassName(hwnd)
                    is_min = bool(win32gui.IsIconic(hwnd))
                    try:
                        rect = win32gui.GetWindowRect(hwnd)
                    except Exception:
                        rect = (0, 0, 0, 0)
                    results.append(
                        WindowDetail(
                            hwnd=hwnd,
                            title=title,
                            class_name=cls_name,
                            is_visible=True,
                            is_minimized=is_min,
                            is_maximized=False,
                            rect=rect,
                        )
                    )

        try:
            win32gui.EnumWindows(enum_cb, None)
        except Exception:
            pass
        return results

    def focus(self, identifier: int | str) -> ActionResult:
        from jarvis.actions.window import activate_window

        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return ActionResult.failure("focus_window", ActionErrorCode.NOT_FOUND, detail=f"Window {identifier!r} not found")

        ok = activate_window(hwnd)
        return ActionResult.success("focus_window", detail=f"Focused window {hwnd}") if ok else ActionResult.failure("focus_window", ActionErrorCode.ACTION_FAILED, detail=f"Failed to focus window {hwnd}")

    def resize(self, identifier: int | str, width: int, height: int) -> ActionResult:
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return ActionResult.failure("resize_window", ActionErrorCode.NOT_FOUND, detail=f"Window {identifier!r} not found")

        if sys.platform != "win32" or self.mock:
            return ActionResult.success("resize_window", detail=f"Resized window {hwnd} to {width}x{height} (simulated)")

        import win32gui
        import win32con

        try:
            rect = win32gui.GetWindowRect(hwnd)
            win32gui.SetWindowPos(hwnd, 0, rect[0], rect[1], width, height, win32con.SWP_NOZORDER | win32con.SWP_NOMOVE)
            return ActionResult.success("resize_window", detail=f"Resized window {hwnd} to {width}x{height}")
        except Exception as e:
            return ActionResult.failure("resize_window", ActionErrorCode.ACTION_FAILED, detail=str(e))

    def move(self, identifier: int | str, x: int, y: int) -> ActionResult:
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return ActionResult.failure("move_window", ActionErrorCode.NOT_FOUND, detail=f"Window {identifier!r} not found")

        if sys.platform != "win32" or self.mock:
            return ActionResult.success("move_window", detail=f"Moved window {hwnd} to ({x}, {y}) (simulated)")

        import win32gui
        import win32con

        try:
            rect = win32gui.GetWindowRect(hwnd)
            w = rect[2] - rect[0]
            h = rect[3] - rect[1]
            win32gui.SetWindowPos(hwnd, 0, x, y, w, h, win32con.SWP_NOZORDER | win32con.SWP_NOSIZE)
            return ActionResult.success("move_window", detail=f"Moved window {hwnd} to ({x}, {y})")
        except Exception as e:
            return ActionResult.failure("move_window", ActionErrorCode.ACTION_FAILED, detail=str(e))

    def minimize(self, identifier: int | str) -> ActionResult:
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return ActionResult.failure("minimize_window", ActionErrorCode.NOT_FOUND, detail=f"Window {identifier!r} not found")

        if sys.platform != "win32" or self.mock:
            return ActionResult.success("minimize_window", detail=f"Minimized window {hwnd} (simulated)")

        import win32gui
        import win32con

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            return ActionResult.success("minimize_window", detail=f"Minimized window {hwnd}")
        except Exception as e:
            return ActionResult.failure("minimize_window", ActionErrorCode.ACTION_FAILED, detail=str(e))

    def maximize(self, identifier: int | str) -> ActionResult:
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return ActionResult.failure("maximize_window", ActionErrorCode.NOT_FOUND, detail=f"Window {identifier!r} not found")

        if sys.platform != "win32" or self.mock:
            return ActionResult.success("maximize_window", detail=f"Maximized window {hwnd} (simulated)")

        import win32gui
        import win32con

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return ActionResult.success("maximize_window", detail=f"Maximized window {hwnd}")
        except Exception as e:
            return ActionResult.failure("maximize_window", ActionErrorCode.ACTION_FAILED, detail=str(e))

    def restore(self, identifier: int | str) -> ActionResult:
        hwnd = self._resolve_hwnd(identifier)
        if not hwnd:
            return ActionResult.failure("restore_window", ActionErrorCode.NOT_FOUND, detail=f"Window {identifier!r} not found")

        if sys.platform != "win32" or self.mock:
            return ActionResult.success("restore_window", detail=f"Restored window {hwnd} (simulated)")

        import win32gui
        import win32con

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            return ActionResult.success("restore_window", detail=f"Restored window {hwnd}")
        except Exception as e:
            return ActionResult.failure("restore_window", ActionErrorCode.ACTION_FAILED, detail=str(e))

    def _resolve_hwnd(self, identifier: int | str) -> int | None:
        if isinstance(identifier, int) and identifier > 0:
            return identifier
        query = str(identifier).lower()
        windows = self.list_windows()
        for w in windows:
            if query in w.title.lower():
                return w.hwnd
        return None

