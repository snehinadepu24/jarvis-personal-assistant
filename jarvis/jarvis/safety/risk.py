from __future__ import annotations

import re
from dataclasses import dataclass

from jarvis.core.schema import Screen, Step
from jarvis.safety.denylist import is_denied

DANGEROUS_NAME_RE = re.compile(
    r"\b(send|delete|remove|pay|purchase|checkout|upload|publish|install|uninstall|"
    r"sign ?out|revoke|transfer|approve|submit|format|factory reset)\b",
    re.I,
)
CONFIRM_WINDOW_RE = re.compile(r"\b(confirm|are you sure|overwrite|replace|warning)\b", re.I)

CONNECTOR_TIERS = {
    "files.read": 0, "files.list": 0, "files.rename": 2, "files.write": 3,
    "files.delete": 3, "graph.draft": 2, "graph.send": 3, "graph.teams_post": 3,
    "office.excel_set": 2, "office.outlook_draft": 2, "office.outlook_send": 3,
    "ps.run": 3, "browser.act": 1, "spotify.play": 2,
}

MCP_TIERS: dict[str, int] = {}


def set_mcp_tiers(tiers: dict[str, int]) -> None:
    MCP_TIERS.clear()
    MCP_TIERS.update(tiers)

HOTKEY_SAFE_EXACT = {"^a", "^c", "^v", "^f", "{ESC}", "{F5}", "^{HOME}"}


@dataclass
class Risk:
    """
    Risk assessment result using protocol-defined tiers.
    
    tier: RiskTier enum value (SAFE=0, LOW=1, MEDIUM=2, HIGH=3, CRITICAL=4)
    reason: Explanation of risk classification
    denied: If True, action should be blocked
    """
    tier: int  # Should be RiskTier value
    reason: str
    denied: bool = False
    target_key: str = ""
    window: str = ""
    element_desc: str = ""


def _element_risk(action_type: str, elem, window_title: str) -> Risk:
    label = f'{elem.role} "{elem.name}"'
    if elem.is_password and action_type in ("type", "clear"):
        return Risk(4, f"never type into or clear a password field ({label})", denied=True, element_desc=label, window=window_title)
    name_hit = DANGEROUS_NAME_RE.search(elem.name or "")
    if name_hit:
        return Risk(3, f'element name contains dangerous verb "{name_hit.group(0)}" ({label})', element_desc=label, window=window_title)
    if elem.state.get("expanded") == "true" and action_type == "expand":
        return Risk(1, "already expanded", element_desc=label, window=window_title)
    tier_by_type = {
        "click": 1, "double_click": 1, "right_click": 1, "select_item": 1, "expand": 1,
        "collapse": 1, "scroll": 1, "type": 1,
        "toggle": 2, "clear": 2,
    }
    return Risk(tier_by_type.get(action_type, 2), label, element_desc=label, window=window_title)


def classify(step: Step, screen: Screen) -> Risk:
    """
    Classify action risk tier using protocol-defined RiskTier enum.
    
    Returns Risk with tier value from RiskTier:
    - RiskTier.SAFE (0): No confirmation needed
    - RiskTier.LOW (1): Auto-approve if policy allows  
    - RiskTier.MEDIUM (2): Notify user
    - RiskTier.HIGH (3): Explicit confirmation required
    - RiskTier.CRITICAL (4): Strong confirmation or deny
    """
    a = step.action
    t = a.type
    win_title = screen.window_title
    denied = is_denied(title=win_title)
    if denied:
        return Risk(4, f"deny-listed window: {denied}", denied=True, window=win_title)

    if t in ("done", "fail", "wait", "ask_user"):
        return Risk(RiskTier.SAFE, f"{t}")
    if t == "scroll":
        return Risk(RiskTier.LOW, "scroll is reversible")

    element_types = {"click", "double_click", "right_click", "type", "clear", "select_item", "toggle", "expand", "collapse"}
    if t in element_types:
        mark = getattr(a, "mark", None)
        elem = screen.by_mark(mark) if mark is not None else None
        if elem is None:
            return Risk(4, f"target mark {mark} missing from current screen; cannot re-validate", denied=True, window=win_title)
        risk = _element_risk(t, elem, win_title)
        if CONFIRM_WINDOW_RE.search(win_title) and risk.tier < 3:
            risk.tier = 3
            risk.reason = f"confirmation dialog ({risk.reason})"
        risk.target_key = elem.key
        return risk

    if t == "hotkey":
        keys = a.keys.strip()
        if keys.lower() in HOTKEY_SAFE_EXACT:
            return Risk(1, f"safe hotkey {keys}")
        if any(d in keys.lower() for d in ("{DEL}", "{BS}")) and "^" not in keys.lower():
            return Risk(3, f"destructive hotkey {keys}", window=win_title)
        return Risk(2, f"hotkey {keys}", window=win_title)

    if t == "focus_window":
        return Risk(1, f"focus window containing {a.title_contains!r}")
    if t == "open_app":
        return Risk(1, f"open app {a.name!r}")
    if t == "open_url":
        url = a.url.lower()
        if url.startswith(("http://", "https://", "ms-settings:")):
            return Risk(1, f"open {a.url}")
        return Risk(3, f"non-allowlisted URL scheme: {a.url}", window=win_title)
    if t == "run_powershell":
        from jarvis.connectors.powershell import classify_script

        if classify_script(a.script) == 4:
            return Risk(4, "script matches a deny pattern (default deny)", denied=True, window=win_title)
        return Risk(3, "run_powershell is tier 3 by definition", window=win_title)
    if t == "connector_call":
        tier = CONNECTOR_TIERS.get(a.tool, MCP_TIERS.get(a.tool, 3))
        return Risk(tier, f"connector {a.tool}", window=win_title)
    return Risk(3, f"unclassified action {t}", window=win_title)
