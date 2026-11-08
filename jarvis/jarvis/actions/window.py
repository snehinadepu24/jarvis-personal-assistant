from __future__ import annotations

import sys
import time

if sys.platform != "win32":
    def activate_window(hwnd: int) -> bool:
        return True
else:
    import win32con
    import win32gui
    import win32process

    def activate_window(hwnd: int) -> bool:
        """Escalating activation for a target window handle (HWND)."""
        if not win32gui.IsWindow(hwnd):
            return False

        # If minimized, restore it
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        else:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

        # Attempt 1: Standard SetForegroundWindow
        try:
            win32gui.SetForegroundWindow(hwnd)
            if win32gui.GetForegroundWindow() == hwnd:
                return True
        except Exception:
            pass

        # Attempt 2: AttachThreadInput bypass
        try:
            cur_thread = win32process.GetCurrentThreadId()
            fg_hwnd = win32gui.GetForegroundWindow()
            fg_thread, _ = win32process.GetWindowThreadProcessId(fg_hwnd)

            import ctypes
            user32 = ctypes.windll.user32
            if fg_thread != cur_thread:
                user32.AttachThreadInput(fg_thread, cur_thread, True)
                win32gui.SetForegroundWindow(hwnd)
                user32.AttachThreadInput(fg_thread, cur_thread, False)
            else:
                win32gui.SetForegroundWindow(hwnd)

            time.sleep(0.05)
            return win32gui.GetForegroundWindow() == hwnd
        except Exception:
            return False
