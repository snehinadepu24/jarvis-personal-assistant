from __future__ import annotations

import asyncio
import re

DENY_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"remove-item\s+.*-recurse", r"set-executionpolicy", r"reg\s+add\s+hklm",
        r"\biex\b", r"invoke-expression", r"-encodedcommand", r"-verb\s+runas",
        r"set-mppreference", r"stop-process\s+-name\s+(windefend|security)",
        r"format-volume", r"clear-disk",
    )
]


def classify_script(script: str) -> int:
    if any(p.search(script) for p in DENY_PATTERNS):
        return 4
    return 3


async def run_powershell(script: str, timeout_s: float = 20.0, output_cap: int = 64 * 1024) -> dict:
    tier = classify_script(script)
    if tier == 4:
        return {"ok": False, "tier": 4, "detail": "script matches a deny pattern; force tier 4 / default deny"}
    proc = await asyncio.create_subprocess_exec(
        "pwsh", "-NoProfile", "-NonInteractive", "-Command", script,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    except TimeoutError:
        proc.kill()
        return {"ok": False, "tier": tier, "detail": f"timed out after {timeout_s}s"}
    return {
        "ok": proc.returncode == 0,
        "tier": tier,
        "returncode": proc.returncode,
        "output": out[:output_cap].decode("utf-8", "replace"),
    }
