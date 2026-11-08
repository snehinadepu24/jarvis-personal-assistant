from __future__ import annotations

KNOWN_OPAQUE = {
    "DirectUIHWND",
    "SunAwtWindow",
    "Windows.UI.Core.CoreWindow",
    "JavaFWHWND",
}


def uia_confidence(screen) -> float:
    n = len(screen.elements)
    if n == 0:
        return 0.0
    named = sum(bool(e.name) for e in screen.elements) / n
    actionable = sum(bool(e.patterns) for e in screen.elements) / n
    custom = sum(e.role in ("custom", "pane") for e in screen.elements) / n
    s = 0.35 * named + 0.30 * actionable + 0.25 * screen.coverage_ratio - 0.30 * custom
    if screen.window_class in KNOWN_OPAQUE:
        s -= 0.5
    return max(0.0, min(1.0, s))


def choose_route(
    confidence: float,
    need_visual: bool = False,
    verify_failures: int = 0,
    route3_failures: int = 0,
    allow_vlm: bool = True,
    route2_threshold: float = 0.55,
) -> tuple[int, str]:
    if need_visual or verify_failures >= 2:
        if allow_vlm and route3_failures >= 2:
            return 4, "route 3 failed twice; VLM allowed"
        return 3, f"need_visual or repeated verify failure (conf was {confidence:.2f})"
    if confidence >= route2_threshold:
        return 2, f"UIA confidence {confidence:.2f} >= {route2_threshold}"
    return 3, f"confidence {confidence:.2f} < {route2_threshold}"
