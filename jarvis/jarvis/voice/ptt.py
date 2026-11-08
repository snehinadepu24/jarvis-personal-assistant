from __future__ import annotations

import sys

if sys.platform != "win32":
    raise ImportError("ptt.py is Windows-only (pynput global hook)")

import threading

from pynput import keyboard

HOTKEYS = ("<ctrl_l>+<space>", "<ctrl_r>+<space>")


class PushToTalk:
    def __init__(self, on_start, on_stop):
        self.on_start = on_start
        self.on_stop = on_stop
        self._recording = False

    def run(self) -> None:
        with keyboard.GlobalHotKeys({hotkey: self._toggle for hotkey in HOTKEYS}) as h:
            h.join()

    def _toggle(self):
        if self._recording:
            self._recording = False
            self.on_stop()
        else:
            self._recording = True
            threading.Thread(target=self.on_start, daemon=True).start()
