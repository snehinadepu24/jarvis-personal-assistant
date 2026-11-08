from __future__ import annotations

import re

from jarvis.core.schema import Screen

PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"ignore (all )?(previous|prior|above) (instructions|rules|prompts)", re.I), "override instruction"),
    (re.compile(r"disregard (all )?(previous|prior|your)", re.I), "override instruction"),
    (re.compile(r"(email|send|forward|exfiltrate|upload).{0,40}\b(to|at)\b.{0,40}@", re.I | re.S), "data exfiltration"),
    (re.compile(r"powershell|\bcmd\.exe\b|-encodedcommand|\biex\b|invoke-expression", re.I), "command execution"),
    (re.compile(r"\b(curl|wget)\s+https?://", re.I), "network command"),
    (re.compile(r"approve (all|every|this|any)", re.I), "consent harvesting"),
    (re.compile(r"(reveal|show|paste|share).{0,30}(password|otp|card|credential|api ?key|token)", re.I), "secret harvesting"),
    (re.compile(r"wire (transfer|money)|gift card", re.I), "fraud"),
    (re.compile(r"https?://\S+\.(ru|xyz|top)\b", re.I), "suspicious url"),
]


def scan_screen(screen: Screen) -> list[dict]:
    flags = []
    for e in screen.elements:
        blob = " ".join(filter(None, [e.name, e.value or ""]))
        if not blob:
            continue
        reasons = [why for pat, why in PATTERNS if pat.search(blob)]
        if reasons:
            flags.append({"mark": e.mark, "reasons": reasons, "sample": blob[:120]})
    return flags
