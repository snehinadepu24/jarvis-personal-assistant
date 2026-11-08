from __future__ import annotations

import hashlib
import json
import re

DENY_EXE = {
    "consent.exe", "credentialuibroker.exe", "logonui.exe", "osk.exe",
    "windowssecurity", "securityhealthservice",
}

DENY_TITLE_PATTERNS = [
    re.compile(p, re.I)
    for p in (
        r"windows security", r"bitlocker", r"user account control", r"credential",
        r"sign-?in options", r"windows hello", r"password manager",
        r"1password", r"bitwarden", r"keepass", r"lastpass", r"dashlane", r"enpass",
        r"bank", r"\bvpn\b.*settings", r"windows defender",
    )
]

DENY_URLS = {"ms-settings:signinoptions", "ms-settings:windowsdefender"}


def is_denied(title: str = "", process: str = "", url: str = "") -> str | None:
    if process and process.lower() in DENY_EXE:
        return f"process {process}"
    for pat in DENY_TITLE_PATTERNS:
        if pat.search(title or ""):
            return f"title {title!r}"
    if (url or "").lower() in DENY_URLS:
        return f"url {url}"
    return None


def action_fingerprint(action_json: dict, target_key: str, window_title: str) -> str:
    basis = json.dumps({"action": action_json, "target": target_key, "window": window_title}, sort_keys=True)
    return hashlib.sha256(basis.encode()).hexdigest()[:16]
