from __future__ import annotations

from jarvis.actions.base import ActionResult
from jarvis.core.schema import (
    ActionErrorCode,
    AskUser,
    AskUserPending,
    Clear,
    Click,
    Connector,
    Done,
    Expand,
    Fail,
    FocusWindow,
    Hotkey,
    OpenApp,
    OpenUrl,
    RunPS,
    Screen,
    Scroll,
    SelectItem,
    SetText,
    Step,
    Toggle,
    Wait,
)


class MockExecutor:
    name = "mock-executor"

    def __init__(self, desktop, files_connector=None, mcp_registry=None):
        self.desktop = desktop
        self.files = files_connector
        self.mcp = mcp_registry

    async def apply(self, step: Step, screen=None) -> ActionResult:
        a = step.action

        # Check for stale snapshot reference
        if screen is not None and getattr(a, "snapshot_id", None) and getattr(screen, "snapshot_id", None):
            if a.snapshot_id != screen.snapshot_id:
                return ActionResult.stale_target(
                    command=a.type,
                    ref=getattr(a, "ref", "") or "",
                    snapshot_id=a.snapshot_id,
                )

        # Resolve ref to mark if mark is 0 or unset
        if screen is not None and getattr(a, "ref", None) and getattr(a, "mark", 0) == 0:
            target_el = screen.by_ref(a.ref)
            if target_el is not None:
                a.mark = target_el.mark

        try:
            if isinstance(a, (Done, Fail, AskUser, Wait)):
                return ActionResult.success(a.type, detail=a.type)
            if isinstance(a, Click):
                res = self._click(a)
            elif isinstance(a, SetText):
                res = self._set_text(a)
            elif isinstance(a, Clear):
                res = self._clear(a)
            elif isinstance(a, SelectItem):
                res = self._select(a)
            elif isinstance(a, Toggle):
                res = self._toggle(a)
            elif isinstance(a, Expand):
                res = self._expand(a)
            elif isinstance(a, Scroll):
                res = ActionResult.success("scroll", detail=f"scrolled {a.direction}")
            elif isinstance(a, Hotkey):
                res = self._hotkey(a)
            elif isinstance(a, FocusWindow):
                ok = self.desktop.focus_window(a.title_contains)
                detail = f"focused {a.title_contains}" if ok else f"no window matching {a.title_contains!r}"
                res = ActionResult.success("focus_window", detail=detail) if ok else ActionResult.failure("focus_window", ActionErrorCode.NOT_FOUND, detail=detail)
            elif isinstance(a, OpenApp):
                ok = self.desktop.open_app(a.name)
                detail = f"opened app {a.name}" if ok else f"app {a.name!r} not found"
                res = ActionResult.success("open_app", detail=detail) if ok else ActionResult.failure("open_app", ActionErrorCode.NOT_FOUND, detail=detail)
            elif isinstance(a, OpenUrl):
                res = self._open_url(a)
            elif isinstance(a, RunPS):
                res = ActionResult.success("run_powershell", detail="simulated powershell run (mock backend)")
            elif isinstance(a, Connector):
                res = await self._connector(a)
            else:
                res = ActionResult.failure(a.type, ActionErrorCode.UNSUPPORTED, detail=f"unsupported action {a.type}")

            # Ensure envelope exists
            if res.envelope is None:
                if res.ok:
                    res = ActionResult.success(a.type, detail=res.detail, artifact=res.artifact, input_mode=res.input_mode)
                else:
                    res = ActionResult.failure(a.type, detail=res.detail, artifact=res.artifact, input_mode=res.input_mode)
            return res
        except AskUserPending:
            raise

    def _el(self, mark: int):
        screen = self.desktop.observe()
        el = screen.by_mark(mark)
        if el is None:
            raise KeyError(f"mark {mark} not on screen")
        return screen, el

    def _click(self, a: Click) -> ActionResult:
        screen, el = self._el(a.mark)
        w = self.desktop.windows[self.desktop.active_wid]
        d = w.elements[el.automation_id]
        if "invoke" in d["patterns"]:
            if el.automation_id == "send-btn":
                self.desktop.teams_send_invoked = True
            self.desktop.touch()
            return ActionResult.success("click", detail=f"invoked {el.name!r}", input_mode="semantic")
        if "selectitem" in d["patterns"]:
            for other in w.elements.values():
                if "selectitem" in other["patterns"]:
                    other["state"]["selected"] = "false"
            d["state"]["selected"] = "true"
            self.desktop.touch()
            return ActionResult.success("click", detail=f"selected {el.name!r}", input_mode="semantic")
        if "toggle" in d["patterns"]:
            new = "off" if d["state"].get("toggle") == "on" else "on"
            d["state"]["toggle"] = new
            if el.automation_id == "bluetooth-toggle":
                self.desktop.bluetooth_on = new == "on"
            self.desktop.touch()
            return ActionResult.success("click", detail=f"toggled {el.name!r} -> {new}", input_mode="semantic")
        self.desktop.touch()
        return ActionResult.success("click", detail=f"clicked {el.name!r}", input_mode="semantic")

    def _set_text(self, a: SetText) -> ActionResult:
        screen, el = self._el(a.mark)
        w = self.desktop.windows[self.desktop.active_wid]
        d = w.elements[el.automation_id]
        if "value" not in d["patterns"]:
            return ActionResult.failure("type", ActionErrorCode.UNSUPPORTED, detail=f"{el.name!r} has no Value pattern")
        d["value"] = a.text
        if el.automation_id == "find-box" and a.submit:
            count = self.desktop.find_count(a.text)
            return ActionResult.success("type", detail=f"find {a.text!r}: {count} matches", artifact={"find_count": count})
        self.desktop.touch()
        if a.submit:
            res = self.desktop.submit_active()
            if "find_count" in res:
                return ActionResult.success("type", detail=f"find {a.text!r}: {res['find_count']} matches", artifact=res)
            if "needs_confirm" in res:
                return ActionResult.success("type", detail="overwrite confirmation dialog opened", artifact=res)
            return ActionResult.success("type", detail="typed + submit", artifact=res)
        return ActionResult.success("type", detail=f"set text in {el.name!r}")

    def _clear(self, a: Clear) -> ActionResult:
        screen, el = self._el(a.mark)
        w = self.desktop.windows[self.desktop.active_wid]
        w.elements[el.automation_id]["value"] = ""
        self.desktop.touch()
        return ActionResult.success("clear", detail=f"cleared {el.name!r}")

    def _select(self, a: SelectItem) -> ActionResult:
        screen, el = self._el(a.mark)
        w = self.desktop.windows[self.desktop.active_wid]
        if a.item:
            target = next((e for e in w.elements.values() if e["name"].lower() == a.item.lower()), None)
            if target is None:
                return ActionResult.failure("select_item", ActionErrorCode.NOT_FOUND, detail=f"item {a.item!r} not found")
            for other in w.elements.values():
                if "selectitem" in other["patterns"]:
                    other["state"]["selected"] = "false"
            target["state"]["selected"] = "true"
            self.desktop.touch()
            return ActionResult.success("select_item", detail=f"selected {a.item!r}")
        return ActionResult.success("select_item", detail=f"selected {el.name!r}")

    def _toggle(self, a: Toggle) -> ActionResult:
        screen, el = self._el(a.mark)
        w = self.desktop.windows[self.desktop.active_wid]
        d = w.elements[el.automation_id]
        if "toggle" not in d["patterns"]:
            return ActionResult.failure("toggle", ActionErrorCode.UNSUPPORTED, detail=f"{el.name!r} has no Toggle pattern")
        for _ in range(2):
            cur = d["state"].get("toggle", "off")
            if a.desired is None or cur == a.desired:
                break
            d["state"]["toggle"] = "on" if cur == "off" else "off"
            if el.automation_id == "bluetooth-toggle":
                self.desktop.bluetooth_on = d["state"]["toggle"] == "on"
        self.desktop.touch()
        return ActionResult.success("toggle", detail=f"toggle {el.name!r} now {d['state'].get('toggle')}")

    def _expand(self, a: Expand) -> ActionResult:
        screen, el = self._el(a.mark)
        w = self.desktop.windows[self.desktop.active_wid]
        w.elements[el.automation_id]["state"]["expanded"] = "true" if a.type == "expand" else "false"
        self.desktop.touch()
        return ActionResult.success(a.type, detail=f"{a.type} {el.name!r}")

    def _hotkey(self, a: Hotkey) -> ActionResult:
        res = self.desktop.hotkey(a.keys)
        self.desktop.touch()
        return ActionResult.success("hotkey", detail=f"hotkey {a.keys}: {res}", artifact=res)

    def _open_url(self, a: OpenUrl) -> ActionResult:
        url = a.url
        if url.startswith("ms-settings:"):
            ok = self.desktop.focus_window("Settings") or self.desktop.open_app("Settings")
            detail = f"opened {url}" if ok else "Settings not available"
            return ActionResult.success("open_url", detail=detail) if ok else ActionResult.failure("open_url", ActionErrorCode.NOT_FOUND, detail=detail)
        if not url.lower().startswith(("http://", "https://")):
            return ActionResult.failure("open_url", ActionErrorCode.INVALID_ARGS, detail=f"scheme not allowed: {url}")
        self.desktop.open_app("Google Chrome")
        self.desktop.navigate(url)
        return ActionResult.success("open_url", detail=f"navigated to {url}")

    async def _connector(self, a: Connector) -> ActionResult:
        if a.tool.startswith("mcp.") and self.mcp is not None:
            _, server, tool = a.tool.split(".", 2)
            try:
                result = await self.mcp.call(server, tool, a.args)
                ok = not result.get("is_error", True)
                content = "; ".join(result.get("content", []))[:200]
                detail = f"mcp {server}.{tool}: {content}"
                return ActionResult.success("connector_call", data=result, detail=detail, artifact={"mcp": result}) if ok else ActionResult.failure("connector_call", ActionErrorCode.ACTION_FAILED, detail=detail, artifact={"mcp": result})
            except KeyError:
                return ActionResult.failure("connector_call", ActionErrorCode.NOT_FOUND, detail=f"unknown MCP server {server!r}")
        if a.tool.startswith("files.") and self.files is not None:
            return self.files.handle(a.tool, a.args)
        return ActionResult.failure("connector_call", ActionErrorCode.NOT_FOUND, detail=f"connector {a.tool} not registered in this environment")
