from __future__ import annotations

import sys
import time

if sys.platform != "win32":
    raise ImportError("events.py is Windows-only (comtypes UIA event handlers)")

from comtypes import COMObject  # noqa: E402

from comtypes.gen import UIAutomationClient as UIA  # noqa: E402

_last = time.monotonic()


def last_event_time() -> float:
    return _last


class Events(COMObject):
    _com_interfaces_ = [
        UIA.IUIAutomationStructureChangedEventHandler,
        UIA.IUIAutomationFocusChangedEventHandler,
    ]

    def HandleStructureChangedEvent(self, sender, changeType, runtimeId):
        global _last
        _last = time.monotonic()

    def HandleFocusChangedEvent(self, sender):
        global _last
        _last = time.monotonic()


def install_events(ctx, hwnd):
    ctx.ev = Events()
    root = ctx.uia.ElementFromHandle(hwnd)
    ctx.uia.AddStructureChangedEventHandler(root, UIA.TreeScope_Subtree, None, ctx.ev)
    ctx.uia.AddFocusChangedEventHandler(None, ctx.ev)
    return root


def remove_events(ctx, root):
    try:
        ctx.uia.RemoveStructureChangedEventHandler(root, ctx.ev)
        ctx.uia.RemoveAllEventHandlers()
    except Exception:
        pass


async def wait_idle_polling(hash_window, timeout: float = 5.0, idle_ms: float = 300) -> bool:
    import asyncio
    import struct

    def gray64_hash(img) -> str:
        import hashlib

        return hashlib.blake2s(bytes(img[:64, :64].tobytes()), digest_size=8).hexdigest() if img.size else ""

    loop = asyncio.get_running_loop()
    t0 = loop.time()
    prev = None
    while loop.time() - t0 < timeout:
        h = hash_window()
        if h and h == prev and time.monotonic() - last_event_time() > idle_ms / 1000:
            return True
        prev = h
        await asyncio.sleep(0.15)
    return False
