from __future__ import annotations

from dataclasses import dataclass, field

from jarvis.core.schema import Screen


@dataclass
class Diff:
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)

    @property
    def empty(self) -> bool:
        return not (self.added or self.removed or self.changed)

    def line(self) -> str:
        if self.empty:
            return "(no changes)"
        parts = []
        if self.added:
            parts.append(f"added {len(self.added)}")
        if self.removed:
            parts.append(f"removed {len(self.removed)}")
        if self.changed:
            parts.append(f"changed {len(self.changed)}")
        return ", ".join(parts)


def _sig(e) -> tuple:
    return (e.name, e.value, e.enabled, e.focused, tuple(sorted(e.state.items())))


def screen_diff(before: Screen | None, after: Screen) -> Diff:
    if before is None:
        return Diff(added=[e.key for e in after.elements])
    b = {e.key: e for e in before.elements}
    a = {e.key: e for e in after.elements}
    d = Diff()
    d.added = [k for k in a if k not in b]
    d.removed = [k for k in b if k not in a]
    d.changed = [k for k in a if k in b and _sig(a[k]) != _sig(b[k])]
    return d
