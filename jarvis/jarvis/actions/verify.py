from __future__ import annotations

from dataclasses import dataclass, field

from jarvis.actions.base import ActionResult


@dataclass
class VerifyResult:
    ok: bool
    detail: str = ""
    diff_empty: bool = True


def _rect_center_changed(a, b) -> bool:
    return a is not None and b is not None and a.center() != b.center()


async def verify_step(step, before, after, backend, executor) -> VerifyResult:
    from jarvis.perception.diff import screen_diff

    if after is None:
        return VerifyResult(False, "no screen after action")
    diff = screen_diff(before, after)
    a = step.action
    t = a.type

    if t in ("toggle",):
        target = None
        if before:
            old = before.by_mark(a.mark)
            target = after.by_key(old.key) if old else None
        if target is None:
            return VerifyResult(bool(diff.changed or diff.removed), f"target gone after toggle; diff={diff.line()}", diff.empty)
        state = target.state.get("toggle", "")
        if a.desired:
            return VerifyResult(state == a.desired, f"toggle now {state} (wanted {a.desired})", diff.empty)
        return VerifyResult(diff.changed or state != "", f"toggle now {state}", diff.empty)

    if t == "type":
        old = before.by_mark(a.mark) if before else None
        target = after.by_key(old.key) if old else None
        if target is not None and target.value is not None:
            ok = a.text[:60] in (target.value or "")
            return VerifyResult(ok, f"value now {target.value[:60]!r}", diff.empty)
        return VerifyResult(not diff.empty, f"diff={diff.line()}", diff.empty)

    if t in ("click", "double_click", "right_click", "select_item", "expand", "collapse", "clear"):
        if before:
            old = before.by_mark(a.mark)
            if old and after.by_key(old.key) is None:
                return VerifyResult(True, "element disappeared", diff.empty)
        return VerifyResult(not diff.empty, f"diff={diff.line()}", diff.empty)

    if t in ("focus_window", "open_app", "open_url"):
        if t == "focus_window" and getattr(step, "action", None):
            title = getattr(a, "title_contains", "").lower()
            if title and after.window_title and title in after.window_title.lower():
                return VerifyResult(True, f"window already focused: {after.window_title!r}", False)
        return VerifyResult(not diff.empty, f"diff={diff.line()}", diff.empty)

    if t in ("wait", "scroll", "hotkey"):
        return VerifyResult(True, f"{t} accepted", diff.empty)

    return VerifyResult(not diff.empty, f"generic diff check: {diff.line()}", diff.empty)
