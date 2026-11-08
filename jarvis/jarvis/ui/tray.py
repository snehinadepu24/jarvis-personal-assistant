from __future__ import annotations

import sys

if sys.platform != "win32":
    raise ImportError("tray.py is Windows-only (pystray)")

import threading
from typing import Optional, Callable

import pystray
from PIL import Image

STATE_COLORS = {"listen": "#22C55E", "busy": "#FFB224", "stop": "#FF5D5D", "paused": "#64748B"}


class Tray:
    def __init__(
        self,
        on_listen: Callable[[], None],
        on_stop: Callable[[], None],
        on_pause: Callable[[], None],
        on_quit: Callable[[], None],
        on_toggle_wakeword: Optional[Callable[[bool], None]] = None,
        wakeword_enabled: bool = False,
    ):
        self.wakeword_enabled = wakeword_enabled
        self.on_toggle_wakeword = on_toggle_wakeword

        def toggle_wakeword_action(icon, item):
            self.wakeword_enabled = not self.wakeword_enabled
            if self.on_toggle_wakeword:
                self.on_toggle_wakeword(self.wakeword_enabled)

        def is_wakeword_checked(item):
            return self.wakeword_enabled

        self.menu = pystray.Menu(
            pystray.MenuItem("Listen", on_listen, default=True),
            pystray.MenuItem(
                "Wake Word ('Hey Jarvis')",
                toggle_wakeword_action,
                checked=is_wakeword_checked,
            ),
            pystray.MenuItem("STOP", on_stop),
            pystray.MenuItem("Pause", on_pause),
            pystray.MenuItem("Quit", on_quit),
        )
        self.icon = pystray.Icon("jarvis", self._icon("listen"), "JARVIS", self.menu)

    def _icon(self, state: str) -> Image.Image:
        from PIL import ImageDraw

        img = Image.new("RGB", (64, 64), STATE_COLORS.get(state, "#64748B"))
        ImageDraw.Draw(img).rectangle((12, 28, 52, 36), fill="#0B0F14")
        return img

    def set_state(self, state: str) -> None:
        self.icon.icon = self._icon(state)

    def run(self) -> None:
        self.icon.run_detached()

    def stop(self) -> None:
        self.icon.stop()
