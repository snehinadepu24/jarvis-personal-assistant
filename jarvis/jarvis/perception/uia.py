from __future__ import annotations

import sys

if sys.platform != "win32":
    raise ImportError("uia.py is Windows-only: comtypes UIA on a dedicated MTA thread")

import asyncio
import hashlib
import queue
import threading
import time
import concurrent.futures as cf

import comtypes
import comtypes.client
import win32gui
import win32process

comtypes.client.GetModule("UIAutomationCore.dll")
from comtypes.gen import UIAutomationClient as UIA  # noqa: E402

from jarvis.core.schema import ROLE, Rect, Screen, UiElement, element_key  # noqa: E402

PROPS = [
    "RuntimeId", "Name", "AutomationId", "ControlType", "ClassName", "BoundingRectangle",
    "IsEnabled", "IsOffscreen", "IsPassword", "HasKeyboardFocus", "NativeWindowHandle",
    "IsInvokePatternAvailable", "IsValuePatternAvailable", "IsTogglePatternAvailable",
    "IsSelectionItemPatternAvailable", "IsExpandCollapsePatternAvailable",
    "IsScrollPatternAvailable", "IsScrollItemPatternAvailable",
    "ValueValue", "ToggleToggleState",
]

PAT = {
    "invoke": "IsInvokePatternAvailable", "value": "IsValuePatternAvailable",
    "toggle": "IsTogglePatternAvailable", "select": "IsSelectionItemPatternAvailable",
    "expand": "IsExpandCollapsePatternAvailable", "scroll": "IsScrollPatternAvailable",
    "scrollitem": "IsScrollItemPatternAvailable",
}


class UiaThread:
    def __init__(self):
        self.q: queue.Queue = queue.Queue()
        self.ready = threading.Event()
        self.init_error = None
        threading.Thread(target=self._run, name="uia-mta", daemon=True).start()
        if not self.ready.wait(timeout=5.0):
            print("WARNING: UIA background thread initialization timed out", flush=True)

    def _run(self):
        try:
            try:
                comtypes.CoInitializeEx(comtypes.COINIT_MULTITHREADED)
            except OSError:
                pass
            try:
                self.uia = comtypes.client.CreateObject(UIA.CUIAutomation8, interface=UIA.IUIAutomation)
            except Exception:
                self.uia = comtypes.client.CreateObject(UIA.CUIAutomation, interface=UIA.IUIAutomation)
            cr = self.uia.CreateCacheRequest()
            for p in PROPS:
                try:
                    cr.AddProperty(getattr(UIA, f"UIA_{p}PropertyId"))
                except Exception:
                    pass
            cr.TreeFilter = self.uia.ControlViewCondition
            self.cache = cr
        except Exception as e:
            self.init_error = e
            print(f"JARVIS UIA thread init error: {e}", flush=True)
        finally:
            self.ready.set()
        while True:
            fn, fut = self.q.get()
            try:
                fut.set_result(fn(self))
            except Exception as e:
                fut.set_exception(e)

    def submit(self, fn) -> cf.Future:
        fut = cf.Future()
        self.q.put((fn, fut))
        return fut

    async def submit_async(self, fn):
        return await asyncio.wrap_future(self.submit(fn))


def _is_usable_app_window(h: int) -> bool:
    try:
        if not h or not win32gui.IsWindow(h) or not win32gui.IsWindowVisible(h) or win32gui.IsIconic(h):
            return False
        title = win32gui.GetWindowText(h).strip()
        cls = win32gui.GetClassName(h).lower()
        if not title:
            return False
        if title.startswith("JARVIS") or cls in ("progman", "workerw", "tk", "shell_traywnd"):
            return False
        lower_title = title.lower()
        # Filter floating background utility widgets, overlays, IME or notification windows
        if any(ign in lower_title for ign in ("grammarly", "nvidia overlay", "snippingtool", "system tray")):
            return False
        l, t, r, b = win32gui.GetWindowRect(h)
        # Filter tiny overlay boxes
        if (r - l) < 250 or (b - t) < 150:
            return False
        return True
    except Exception:
        return False


def _app_window(hwnd: int) -> int:
    if hwnd and _is_usable_app_window(hwnd):
        return hwnd

    candidates = []

    def collect(h, _):
        if _is_usable_app_window(h):
            try:
                l, t, r, b = win32gui.GetWindowRect(h)
                area = (r - l) * (b - t)
                candidates.append((area, h))
            except Exception:
                pass

    try:
        win32gui.EnumWindows(collect, None)
    except Exception:
        pass

    if candidates:
        # Sort by window area descending: pick the primary active document/IDE/browser window!
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1]

    desktop = win32gui.GetDesktopWindow()
    return hwnd if (hwnd and win32gui.IsWindow(hwnd) and hwnd != desktop) else desktop


def snapshot_foreground(ctx, max_elems: int = 400):
    desktop = win32gui.GetDesktopWindow()
    hwnd = desktop
    try:
        fg = win32gui.GetForegroundWindow()
        hwnd = _app_window(fg)
        if not hwnd or not win32gui.IsWindow(hwnd):
            hwnd = desktop
        root = ctx.uia.ElementFromHandleBuildCache(hwnd, ctx.cache)
        scope = UIA.TreeScope_Children if hwnd == desktop else UIA.TreeScope_Descendants
        arr = root.FindAllBuildCache(scope, ctx.uia.CreateTrueCondition(), ctx.cache)
    except Exception:
        try:
            root = ctx.uia.GetRootElementBuildCache(ctx.cache)
            arr = root.FindAllBuildCache(UIA.TreeScope_Children, ctx.uia.CreateTrueCondition(), ctx.cache)
            hwnd = desktop
        except Exception:
            return 0, "Desktop", 0, []

    def g(e, p, default=None):
        try:
            return e.GetCachedPropertyValue(getattr(UIA, f"UIA_{p}PropertyId"))
        except (comtypes.COMError, OSError):
            return default

    out = []
    try:
        win_class = win32gui.GetClassName(hwnd)
    except Exception:
        win_class = "Desktop"
    length = getattr(arr, "Length", 0) if arr is not None else 0
    for i in range(min(length, 3000)):
        try:
            e = arr.GetElement(i)
            r = e.CachedBoundingRectangle
            name = (e.CachedName or "").strip()
            aid = e.CachedAutomationId or ""
            cls = e.CachedClassName or ""
            ct = e.CachedControlType
            rid = tuple(e.GetRuntimeId() or ())
        except (comtypes.COMError, OSError, Exception):
            continue
        pats = [k for k, p in PAT.items() if g(e, p)]
        pwd = bool(g(e, "IsPassword"))
        if g(e, "IsOffscreen") or r.right - r.left < 2 or r.bottom - r.top < 2:
            continue
        if not pats and not name:
            continue
        if ct in (50025, 50026, 50033) and not pats:
            continue
        out.append(dict(
            name=name[:120], ct=ct, aid=aid, cls=cls,
            rect=(r.left, r.top, r.right, r.bottom),
            enabled=bool(g(e, "IsEnabled", True)),
            focused=bool(g(e, "HasKeyboardFocus")), patterns=pats,
            pwd=pwd,
            value=None if pwd else (str(g(e, "ValueValue") or "")[:60] or None),
            rid=rid,
        ))
    out.sort(key=lambda d: (not d["focused"], not d["patterns"], d["rect"][1], d["rect"][0]))
    try:
        pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    except Exception:
        pid = 0
    return hwnd, win_class, pid, out[:max_elems]


def build_screen(hwnd, win_class, pid, rows) -> Screen:
    from jarvis.perception.serialize import assign_marks, rank

    elems = []
    for d in rows:
        r = d["rect"]
        elems.append(UiElement(
            mark=0, role=ROLE.get(d["ct"], "ctl"), name=d["name"], value=d["value"],
            automation_id=d["aid"], control_type=d["ct"],
            rect=Rect(l=r[0], t=r[1], r=r[2], b=r[3]),
            enabled=d["enabled"], focused=d["focused"], is_password=d["pwd"],
            patterns=d["patterns"], key=element_key(d["aid"], d["ct"], d["name"], win_class),
            selector=[{"automation_id": d["aid"], "control_type": d["ct"]}] if d["aid"]
            else [{"name": d["name"], "control_type": d["ct"]}],
        ))
    ordered = assign_marks(rank(elems))
    try:
        title = win32gui.GetWindowText(hwnd) if hwnd else ""
    except Exception:
        title = ""
    scr = Screen(
        app="", window_title=title, window_class=win_class,
        hwnd=hwnd or 0, pid=pid, elements=ordered,
        focused_mark=next((e.mark for e in ordered if e.focused), None),
        coverage_ratio=min(1.0, sum(e.rect.area() for e in ordered) / max(1, (1 * 1))),
        screenshot_hash=hashlib.blake2s(str([d["name"] for d in rows]).encode(), digest_size=8).hexdigest(),
        ts=time.time(),
    )
    scr.ensure_snapshot_id()
    return scr


class UiaBackend:
    name = "uia"

    def __init__(self, cfg=None):
        self.thread = UiaThread()

    async def observe(self, route: int = 2) -> Screen:
        hwnd, win_class, pid, rows = await self.thread.submit_async(snapshot_foreground)
        return build_screen(hwnd, win_class, pid, rows)

    async def wait_idle(self, timeout: float = 5.0) -> bool:
        from jarvis.perception.events import last_event_time

        loop = asyncio.get_running_loop()
        t0 = loop.time()
        while loop.time() - t0 < timeout:
            if time.monotonic() - last_event_time() > 0.3:
                return True
            await asyncio.sleep(0.05)
        return False

    def list_windows(self) -> list[dict]:
        out = []

        def cb(h, _):
            try:
                if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h):
                    out.append({"wid": h, "title": win32gui.GetWindowText(h), "cls": win32gui.GetClassName(h)})
            except Exception:
                pass

        try:
            win32gui.EnumWindows(cb, None)
        except Exception:
            pass
        return out

    async def screenshot_bytes(self) -> bytes | None:
        import mss
        from io import BytesIO
        from PIL import Image

        try:
            with mss.mss() as s:
                monitor = s.monitors[1] if len(s.monitors) > 1 else s.monitors[0]
                shot = s.grab(monitor)
                image = Image.frombytes("RGB", shot.size, shot.rgb)
                output = BytesIO()
                image.save(output, format="PNG")
                return output.getvalue()
        except Exception as e:
            print(f"JARVIS screenshot error: {e}", flush=True)
            return None
