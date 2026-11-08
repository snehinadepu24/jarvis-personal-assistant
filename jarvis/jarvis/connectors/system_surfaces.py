from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any

from jarvis.actions.base import ActionResult
from jarvis.core.schema import ActionErrorCode


@dataclass
class SystemSurface:
    name: str
    hwnd: int
    rect: tuple[int, int, int, int]
    is_available: bool


class SystemSurfacesConnector:
    name = "system_surfaces"

    def list_surfaces(self) -> list[SystemSurface]:
        surfaces = []
        if sys.platform != "win32":
            return [
                SystemSurface("taskbar", 100, (0, 720, 1280, 768), True),
                SystemSurface("tray", 101, (1100, 720, 1280, 768), True),
                SystemSurface("start_menu", 102, (0, 400, 400, 720), True),
                SystemSurface("action_center", 103, (900, 200, 1280, 720), True),
            ]

        import win32gui

        # 1. Main Taskbar
        tb_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
        tb_rect = win32gui.GetWindowRect(tb_hwnd) if tb_hwnd else (0, 0, 0, 0)
        surfaces.append(SystemSurface("taskbar", tb_hwnd or 0, tb_rect, bool(tb_hwnd)))

        # 2. Secondary Taskbars (multi-monitor)
        sec_tb = win32gui.FindWindow("Shell_SecondaryTrayWnd", None)
        if sec_tb:
            surfaces.append(SystemSurface("secondary_taskbar", sec_tb, win32gui.GetWindowRect(sec_tb), True))

        # 3. Notification Area (Tray)
        tray_hwnd = 0
        if tb_hwnd:
            tray_hwnd = win32gui.FindWindowEx(tb_hwnd, 0, "TrayNotifyWnd", None)
        surfaces.append(SystemSurface("tray", tray_hwnd or 0, win32gui.GetWindowRect(tray_hwnd) if tray_hwnd else (0, 0, 0, 0), bool(tray_hwnd)))

        # 4. Start Button / Menu
        start_hwnd = win32gui.FindWindow("Start", None) or win32gui.FindWindow("Windows.UI.Core.CoreWindow", "Start")
        surfaces.append(SystemSurface("start_menu", start_hwnd or 0, win32gui.GetWindowRect(start_hwnd) if start_hwnd else (0, 0, 0, 0), bool(start_hwnd)))

        return surfaces

    def open_start(self) -> ActionResult:
        if sys.platform != "win32":
            return ActionResult.success("open_start", detail="Opened Start menu (simulated)")

        import win32api
        import win32con

        # Press and release Windows key (VK_LWIN = 0x5B)
        win32api.keybd_event(0x5B, 0, 0, 0)
        win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)
        return ActionResult.success("open_start", detail="Triggered Start menu via Windows key")

    def open_action_center(self) -> ActionResult:
        if sys.platform != "win32":
            return ActionResult.success("open_action_center", detail="Opened Action Center (simulated)")

        import win32api
        import win32con

        # Win + A
        win32api.keybd_event(0x5B, 0, 0, 0)
        win32api.keybd_event(ord("A"), 0, 0, 0)
        win32api.keybd_event(ord("A"), 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(0x5B, 0, win32con.KEYEVENTF_KEYUP, 0)
        return ActionResult.success("open_action_center", detail="Triggered Action Center via Win+A")

