from __future__ import annotations

from jarvis.core.schema import ROLE, Screen, UiElement

TOKEN_BUDGET = 2500
CHARS_PER_TOKEN = 4
MAX_ELEMENTS = 220
MAX_NAME = 120
MAX_VALUE = 60


def rank(elems: list[UiElement]) -> list[UiElement]:
    def priority(e: UiElement):
        is_interactive = bool(e.patterns) or e.control_type in (50004, 50000, 50002, 50003, 50005, 50030)
        return (not e.focused, not is_interactive, not bool(e.patterns), e.rect.t, e.rect.l)
    return sorted(elems, key=priority)


def assign_marks(elems: list[UiElement]) -> list[UiElement]:
    for i, e in enumerate(elems, 1):
        e.mark = i
    return elems


def _flags(e: UiElement) -> str:
    flags = list(e.patterns)
    if not e.enabled:
        flags.append("disabled")
    if e.focused:
        flags.append("focused")
    if e.is_password:
        flags.append("password")
    if e.ref:
        flags.append(f"ref={e.ref}")
    return ",".join(flags)


def serialize(elems: list[UiElement], token_budget: int = TOKEN_BUDGET) -> tuple[str, int]:
    lines: list[str] = []
    chars = 0
    emitted = 0
    for e in elems:
        if emitted >= MAX_ELEMENTS:
            remaining = len(elems) - emitted
            if remaining > 0 and lines:
                lines.append(f"(+{remaining} more…, use scroll)")
            break
        name = (e.name or "")[:MAX_NAME]
        val = "" if (e.is_password or not e.value) else f' ="{e.value[:MAX_VALUE]}"'
        fl = _flags(e)
        line = f'[{e.mark}] {ROLE.get(e.control_type, "ctl")} "{name}"' \
               f'{" #" + e.automation_id if e.automation_id else ""}{val} {{{fl}}}'
        if chars + len(line) > token_budget * CHARS_PER_TOKEN and lines:
            remaining = len(elems) - emitted
            if remaining > 0:
                lines.append(f"(+{remaining} more…, use scroll)")
            break
        lines.append(line)
        chars += len(line)
        emitted += 1
    return "\n".join(lines), chars // CHARS_PER_TOKEN


def serialize_screen(screen: Screen) -> str:
    screen.ensure_snapshot_id()
    ordered = sorted(screen.elements, key=lambda e: e.mark)
    block, _ = serialize(ordered)
    return block


def serialize_skeleton(screen: Screen, token_budget: int = 1000) -> tuple[str, int]:
    """Two-stage observation Stage 1: Compact skeleton of major surfaces/containers."""
    screen.ensure_snapshot_id()
    lines = [f"[SURFACE SKELETON] snapshot={screen.snapshot_id} window=\"{screen.window_title}\" app=\"{screen.app}\" total_elements={len(screen.elements)}"]
    
    # Identify container or high-level landmarks (Pane, Window, Group, Tab, MenuBar, List, ToolBar)
    containers = [e for e in screen.elements if e.control_type in (50033, 50032, 50026, 50018, 50010, 50008, 50021) or not e.patterns]
    if not containers:
        containers = screen.elements[:30]

    chars = sum(len(l) for l in lines)
    for c in containers[:40]:
        # Count interactive children inside this container's rect
        inside = [e for e in screen.elements if c.rect.l <= e.rect.l and e.rect.r <= c.rect.r and c.rect.t <= e.rect.t and e.rect.b <= c.rect.b and e.mark != c.mark]
        line = f'[{c.mark}] {ROLE.get(c.control_type, "container")} "{c.name}" #{c.automation_id} (rect={c.rect.w}x{c.rect.h}, children={len(inside)}, ref={c.ref})'
        if chars + len(line) > token_budget * CHARS_PER_TOKEN:
            break
        lines.append(line)
        chars += len(line)

    return "\n".join(lines), chars // CHARS_PER_TOKEN


def serialize_subtree(screen: Screen, root_ref_or_mark: str | int, token_budget: int = TOKEN_BUDGET) -> tuple[str, int]:
    """Two-stage observation Stage 2: Detailed interactive elements within a selected subtree or container."""
    screen.ensure_snapshot_id()
    root: UiElement | None = None
    if isinstance(root_ref_or_mark, int):
        root = screen.by_mark(root_ref_or_mark)
    elif isinstance(root_ref_or_mark, str):
        root = screen.by_ref(root_ref_or_mark)

    if root is None:
        return serialize(screen.elements, token_budget=token_budget)

    # Filter elements enclosed by or intersecting root rect
    scoped = [
        e for e in screen.elements
        if (root.rect.l <= e.rect.center()[0] <= root.rect.r and root.rect.t <= e.rect.center()[1] <= root.rect.b)
    ]
    if not scoped:
        scoped = [root]

    ordered = sorted(scoped, key=lambda e: e.mark)
    return serialize(ordered, token_budget=token_budget)
