from __future__ import annotations

import sys

if sys.platform != "win32":
    raise ImportError("uia_executor.py is Windows-only (UIA patterns + SendInput)")

import comtypes

from comtypes.gen import UIAutomationClient as UIA  # noqa: E402
from jarvis.actions.base import ActionResult  # noqa: E402
from jarvis.core.schema import (  # noqa: E402
    AskUser,
    Connector,
    Done,
    Fail,
    FocusWindow,
    Hotkey,
    OpenApp,
    OpenUrl,
    RunPS,
    Wait,
)


def _pat(el, pid, iface):
    if el is None:
        return None
    try:
        if not bool(el):
            return None
    except Exception:
        return None
    try:
        p = el.GetCurrentPattern(pid)
        if not p:
            return None
        try:
            if not bool(p):
                return None
        except Exception:
            return None
        res = p.QueryInterface(iface)
        if not res:
            return None
        try:
            if not bool(res):
                return None
        except Exception:
            return None
        return res
    except Exception:
        return None


def _rect_to_center(rect):
    if rect is None:
        return 0, 0
    if hasattr(rect, "center"):
        return rect.center()
    if hasattr(rect, "left") and hasattr(rect, "right"):
        return (rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2
    if isinstance(rect, (list, tuple)) and len(rect) >= 4:
        return (rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2
    return 0, 0


def mouse_click_center(rect, button: str = "left"):
    import ctypes
    import time

    cx, cy = _rect_to_center(rect)
    if cx <= 0 and cy <= 0:
        return "invalid_rect"

    user32 = ctypes.windll.user32
    sm = user32.GetSystemMetrics
    vx, vy = sm(76), sm(77)
    vw, vh = sm(78), sm(79)
    if vw <= 0:
        vw = sm(0)  # SM_CXSCREEN
    if vh <= 0:
        vh = sm(1)  # SM_CYSCREEN
    nx = int((cx - vx) * 65535 / max(1, vw))
    ny = int((cy - vy) * 65535 / max(1, vh))

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class INPUT(ctypes.Structure):
        class _I(ctypes.Union):
            _fields_ = [("mi", MOUSEINPUT), ("pad", ctypes.c_byte * 64)]

        _fields_ = [("type", ctypes.c_ulong), ("union", _I)]

    def send(flags, mouseData=0):
        inp = INPUT(type=0, union=INPUT._I(mi=MOUSEINPUT(nx, ny, mouseData, flags, 0, None)))
        sent = user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        if sent != 1 and ctypes.get_last_error() == 5:
            raise PermissionError("UIPI blocked SendInput (error 5); report elevation block to user")

    # Move cursor
    send(0x8000 | 0x4000 | 0x0001)
    time.sleep(0.02)

    if button == "left":
        send(0x0002)
        time.sleep(0.02)
        send(0x0004)
    elif button == "right":
        send(0x0008)
        time.sleep(0.02)
        send(0x0010)
    elif button == "double":
        send(0x0002)
        time.sleep(0.02)
        send(0x0004)
        time.sleep(0.04)
        send(0x0002)
        time.sleep(0.02)
        send(0x0004)
    return "mouse"


def act_click(el, fallback_rect=None, button: str = "left"):
    if el is not None:
        try:
            if p := _pat(el, UIA.UIA_InvokePatternId, UIA.IUIAutomationInvokePattern):
                p.Invoke()
                return "invoke"
        except Exception:
            pass
        try:
            if p := _pat(el, UIA.UIA_SelectionItemPatternId, UIA.IUIAutomationSelectionItemPattern):
                p.Select()
                return "select"
        except Exception:
            pass
        try:
            if p := _pat(el, UIA.UIA_TogglePatternId, UIA.IUIAutomationTogglePattern):
                p.Toggle()
                return "toggle"
        except Exception:
            pass
        try:
            if p := _pat(el, UIA.UIA_ExpandCollapsePatternId, UIA.IUIAutomationExpandCollapsePattern):
                p.Collapse() if p.CurrentExpandCollapseState == 1 else p.Expand()
                return "expand"
        except Exception:
            pass
        try:
            if p := _pat(el, UIA.UIA_LegacyIAccessiblePatternId, UIA.IUIAutomationLegacyIAccessiblePattern):
                p.DoDefaultAction()
                return "msaa"
        except Exception:
            pass
        try:
            if p := _pat(el, UIA.UIA_ScrollItemPatternId, UIA.IUIAutomationScrollItemPattern):
                p.ScrollIntoView()
        except Exception:
            pass

    target_rect = fallback_rect
    if target_rect is None and el is not None:
        try:
            target_rect = el.CurrentBoundingRectangle
        except Exception:
            pass

    if target_rect is not None:
        return mouse_click_center(target_rect, button=button)
    return "unclicked"


def act_set_text(el, text, submit, fallback_rect=None):
    from pywinauto.keyboard import send_keys

    # 1. Try UIA ValuePattern if available
    if el is not None:
        try:
            vp = _pat(el, UIA.UIA_ValuePatternId, UIA.IUIAutomationValuePattern)
            if vp and not vp.CurrentIsReadOnly:
                vp.SetValue(text)
                if (vp.CurrentValue or "") == text:
                    if submit:
                        send_keys("{ENTER}")
                    return "value"
        except Exception:
            pass

        try:
            el.SetFocus()
        except Exception:
            pass

    # 2. Focus element by clicking center of bounding rect
    if fallback_rect is not None:
        try:
            mouse_click_center(fallback_rect)
            import time
            time.sleep(0.05)
        except Exception:
            pass

    # 3. Type into control
    try:
        send_keys("^a{BACKSPACE}")
    except Exception:
        pass

    if len(text) < 200:
        send_keys("".join("{%s}" % c if c in "+^%~(){}[]" else c for c in text), with_spaces=True, pause=0.005)
    else:
        clipboard_paste(text)

    if submit:
        send_keys("{ENTER}")
    return "keys"


def clipboard_paste(text):
    import win32clipboard
    import win32con

    old = None
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            old = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, text)
        win32clipboard.CloseClipboard()
    except Exception:
        try:
            win32clipboard.CloseClipboard()
        except Exception:
            pass
    from pywinauto.keyboard import send_keys

    send_keys("^v", pause=0.02)
    if old is not None:
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, old)
            win32clipboard.CloseClipboard()
        except Exception:
            pass


def _resolve_selector(worker, hwnd: int, selector: list[dict]):
    try:
        cur = worker.uia.ElementFromHandle(hwnd)
        if not cur or not bool(cur):
            return None
        resolved = False
        for sel in selector or []:
            cond = None
            if sel.get("automation_id"):
                cond = worker.uia.CreatePropertyCondition(UIA.UIA_AutomationIdPropertyId, sel["automation_id"])
            elif sel.get("name_exact") or sel.get("name"):
                name = sel.get("name_exact") or sel.get("name")
                cond = worker.uia.CreatePropertyCondition(UIA.UIA_NamePropertyId, name)
            if cond is not None:
                try:
                    found = cur.FindFirst(UIA.TreeScope_Descendants, cond)
                    if found is None or not bool(found):
                        return None
                    cur = found
                    resolved = True
                except Exception:
                    return None
            elif "path" in sel:
                walker = worker.uia.ControlViewWalker
                for idx in sel["path"]:
                    try:
                        cur = walker.GetFirstChildElement(cur)
                        for _ in range(int(idx)):
                            if cur is None or not bool(cur):
                                return None
                            cur = walker.GetNextSiblingElement(cur)
                        if cur is None or not bool(cur):
                            return None
                    except Exception:
                        return None
                resolved = True
        return cur if resolved else None
    except Exception:
        return None


class UiaExecutor:
    name = "uia-executor"

    def __init__(self, backend, files_connector=None, snapshot_manager=None, navigation_strategy=None):
        self.backend = backend
        self.thread = backend.thread
        self.files = files_connector
        self.snapshot_manager = snapshot_manager
        self.navigation_strategy = navigation_strategy

    async def apply(self, step, screen=None):
        a = step.action
        if screen is None:
            screen = await self.backend.observe()
        
        # Validate mark if using snapshot manager
        if self.snapshot_manager and hasattr(a, 'mark') and a.mark is not None and a.mark > 0:
            is_valid, reason = self.snapshot_manager.validate_mark(a.mark, screen)
            if not is_valid:
                # Snapshot is stale, refresh required
                return ActionResult(False, f"stale reference ({reason}), needs refresh")
        
        if isinstance(a, (Done, Fail, AskUser, Wait)):
            return ActionResult(True, a.type)
        if isinstance(a, Hotkey):
            from pywinauto.keyboard import send_keys

            send_keys(a.keys)
            return ActionResult(True, f"hotkey {a.keys}")
        if isinstance(a, FocusWindow):
            from jarvis.actions.window import activate_window

            target = next((w for w in self.backend.list_windows() if a.title_contains.lower() in w["title"].lower()), None)
            if not target:
                return ActionResult(False, f"no window matching {a.title_contains!r}")
            import win32gui

            foreground = win32gui.GetForegroundWindow()
            foreground_title = win32gui.GetWindowText(foreground)
            if a.title_contains.lower() in foreground_title.lower():
                return ActionResult(True, f"already focused {foreground_title!r}")
            try:
                activate_window(target["wid"])
            except Exception as error:
                print(f"JARVIS focus warning: {error}", flush=True)
            foreground = win32gui.GetForegroundWindow()
            foreground_title = win32gui.GetWindowText(foreground)
            focused = a.title_contains.lower() in foreground_title.lower()
            if not focused:
                focused = target["title"].lower() in foreground_title.lower()
            return ActionResult(focused, f"focused {target['title']!r}")
        if isinstance(a, OpenApp):
            import os

            clean_name = a.name.lower().replace("-", "").replace(" ", "")
            target = next((
                w for w in self.backend.list_windows()
                if clean_name in w["title"].lower().replace("-", "").replace(" ", "")
            ), None)
            if target:
                from jarvis.actions.window import activate_window
                try:
                    activate_window(target["wid"])
                    return ActionResult(True, f"switched to existing window {target['title']!r}")
                except Exception as err:
                    print(f"JARVIS activate window error: {err}", flush=True)

            try:
                os.startfile(a.name)
                return ActionResult(True, f"opened {a.name}")
            except Exception as e:
                return ActionResult(False, f"could not launch '{a.name}': {e}. Tip: use focus_window if already open.")
        if isinstance(a, OpenUrl):
            if not a.url.lower().startswith(("http://", "https://", "ms-settings:")):
                return ActionResult(False, f"scheme not allowed: {a.url}")
            import os

            try:
                os.startfile(a.url)
                return ActionResult(True, f"opened {a.url}")
            except Exception as e:
                return ActionResult(False, f"could not open url: {e}")
        if isinstance(a, RunPS):
            from jarvis.connectors.powershell import run_powershell

            r = await run_powershell(a.script)
            return ActionResult(r["ok"], r.get("detail") or f"returncode {r.get('returncode')}", r)
        if isinstance(a, Connector):
            if a.tool.startswith("files.") and self.files is not None:
                return self.files.handle(a.tool, a.args)
            return ActionResult(False, f"connector {a.tool} not registered")

        # Special case: typing without a mark (focused window typing)
        if a.type == "type" and (not hasattr(a, 'mark') or a.mark is None or a.mark == 0):
            from pywinauto.keyboard import send_keys
            try:
                # Type directly into focused window
                text = a.text
                if len(text) < 200:
                    send_keys("".join("{%s}" % c if c in "+^%~(){}[]" else c for c in text), with_spaces=True, pause=0.005)
                else:
                    clipboard_paste(text)
                if hasattr(a, 'submit') and a.submit:
                    send_keys("{ENTER}")
                return ActionResult(True, f"typed into focused window: {text[:50]}...")
            except Exception as e:
                return ActionResult(False, f"focused window typing failed: {e}")

        el = screen.by_mark(a.mark)
        if el is None:
            return ActionResult(False, f"mark {a.mark} not on observed screen")

        resolved = None
        try:
            sel = [s for s in el.selector if s.get("automation_id") or s.get("name") or s.get("name_exact")] or el.selector
            resolved = await self.thread.submit_async(lambda w: _resolve_selector(w, screen.hwnd, sel))
        except Exception:
            resolved = None

        try:
            return self._dispatch(resolved, a, el)
        except Exception as err:
            return self._fallback_action(a, el, err)

    def _fallback_action(self, a, el, err):
        t = a.type
        rect = getattr(el, "rect", None)
        if rect:
            if t in ("click", "double_click", "right_click"):
                btn = "right" if t == "right_click" else ("double" if t == "double_click" else "left")
                method = mouse_click_center(rect, button=btn)
                return ActionResult(True, f"clicked via {method} (fallback from {err})")
            if t == "type":
                method = act_set_text(None, a.text, a.submit, fallback_rect=rect)
                return ActionResult(True, f"typed via {method} (fallback from {err})")
        return ActionResult(False, f"action failed: {err}")

    def _dispatch(self, el, a, ui_elem=None):
        t = a.type
        fallback_rect = getattr(ui_elem, "rect", None)
        if t in ("click", "double_click", "right_click"):
            btn = "right" if t == "right_click" else ("double" if t == "double_click" else "left")
            return ActionResult(True, f"clicked via {act_click(el, fallback_rect=fallback_rect, button=btn)}")
        if t == "type":
            return ActionResult(True, f"typed via {act_set_text(el, a.text, a.submit, fallback_rect=fallback_rect)}")
        if t == "clear":
            if el is not None:
                try:
                    vp = _pat(el, UIA.UIA_ValuePatternId, UIA.IUIAutomationValuePattern)
                    if vp:
                        vp.SetValue("")
                        return ActionResult(True, "cleared via value pattern")
                except Exception:
                    pass
            if fallback_rect:
                mouse_click_center(fallback_rect)
                from pywinauto.keyboard import send_keys
                send_keys("^a{BACKSPACE}")
                return ActionResult(True, "cleared via mouse focus & backspace")
            return ActionResult(False, "no Value pattern to clear")
        if t == "toggle":
            p = _pat(el, UIA.UIA_TogglePatternId, UIA.IUIAutomationTogglePattern) if el else None
            if not p and fallback_rect:
                mouse_click_center(fallback_rect)
                return ActionResult(True, "toggled via mouse click")
            if not p:
                return ActionResult(False, "no Toggle pattern")
            for _ in range(3):
                try:
                    state = p.CurrentToggleState
                    if a.desired is None or a.desired == ("on" if state == 1 else "off"):
                        return ActionResult(True, f"toggle now {'on' if state == 1 else 'off'}")
                    p.Toggle()
                except Exception:
                    break
            if fallback_rect:
                mouse_click_center(fallback_rect)
                return ActionResult(True, "toggled via mouse click fallback")
            return ActionResult(False, "toggle did not reach desired state")
        if t == "select_item":
            p = _pat(el, UIA.UIA_SelectionItemPatternId, UIA.IUIAutomationSelectionItemPattern) if el else None
            if p:
                try:
                    p.Select()
                    return ActionResult(True, "selected")
                except Exception:
                    pass
            if fallback_rect:
                mouse_click_center(fallback_rect)
                return ActionResult(True, "selected via mouse click")
            return ActionResult(False, "no SelectionItem pattern")
        if t in ("expand", "collapse"):
            p = _pat(el, UIA.UIA_ExpandCollapsePatternId, UIA.IUIAutomationExpandCollapsePattern) if el else None
            if p:
                try:
                    p.Collapse() if t == "collapse" else p.Expand()
                    return ActionResult(True, t)
                except Exception:
                    pass
            if fallback_rect:
                mouse_click_center(fallback_rect)
                return ActionResult(True, f"{t} via mouse click")
            return ActionResult(False, f"no ExpandCollapse pattern")
        if t == "scroll":
            if el is not None:
                p = _pat(el, UIA.UIA_ScrollPatternId, UIA.IUIAutomationScrollPattern)
                if p:
                    try:
                        amount = 0.5
                        if a.direction == "up":
                            p.ScrollVertical(-amount)
                        elif a.direction == "down":
                            p.ScrollVertical(amount)
                        elif a.direction == "left":
                            p.ScrollHorizontal(-amount)
                        else:
                            p.ScrollHorizontal(amount)
                        return ActionResult(True, f"scrolled {a.direction}")
                    except Exception:
                        pass
            if fallback_rect:
                import ctypes
                cx, cy = _rect_to_center(fallback_rect)
                mouse_click_center(fallback_rect)
                # WHEEL SCROLL
                wheel = 120 if a.direction in ("up", "left") else -120
                ctypes.windll.user32.mouse_event(0x0800, 0, 0, wheel, 0)
                return ActionResult(True, f"scrolled {a.direction} via mouse wheel")
            return ActionResult(False, "no Scroll pattern")
        return ActionResult(False, f"unsupported action {t}")
