from __future__ import annotations

import re
import sys
from jarvis.actions.base import ActionResult
from jarvis.core.schema import ActionErrorCode

# Secret patterns for redaction
REDACTION_PATTERNS = [
    (re.compile(r"sk-[a-zA-Z0-9]{20,}", re.IGNORECASE), "[REDACTED_API_KEY]"),
    (re.compile(r"AIza[0-9A-Za-z\-_]{35}", re.IGNORECASE), "[REDACTED_GOOGLE_KEY]"),
    (re.compile(r"bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
    (re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"), "[REDACTED_CARD_NUMBER]"),
    (re.compile(r'(?:password|secret|pwd)\s*[:=]\s*["\']?([^"\'\s]+)["\']?', re.IGNORECASE), "password=[REDACTED]"),
]


def redact_sensitive(text: str) -> str:
    cleaned = text
    for pattern, replacement in REDACTION_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)
    return cleaned


class SafeClipboardConnector:
    name = "clipboard"

    def __init__(self):
        self._simulated_clipboard: str = ""

    def get_text(self, redact: bool = True) -> str:
        raw = ""
        if sys.platform == "win32":
            try:
                import win32clipboard

                win32clipboard.OpenClipboard()
                try:
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                        raw = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                finally:
                    win32clipboard.CloseClipboard()
            except Exception:
                raw = self._simulated_clipboard
        else:
            raw = self._simulated_clipboard

        if redact:
            return redact_sensitive(raw)
        return raw

    def set_text(self, text: str) -> ActionResult:
        self._simulated_clipboard = text
        if sys.platform == "win32":
            try:
                import win32clipboard

                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
                finally:
                    win32clipboard.CloseClipboard()
                return ActionResult.success("clipboard.set", detail="Clipboard text updated")
            except Exception as e:
                return ActionResult.failure("clipboard.set", ActionErrorCode.ACTION_FAILED, detail=str(e))
        return ActionResult.success("clipboard.set", detail="Clipboard text updated (simulated)")

    def clear(self) -> ActionResult:
        self._simulated_clipboard = ""
        if sys.platform == "win32":
            try:
                import win32clipboard

                win32clipboard.OpenClipboard()
                try:
                    win32clipboard.EmptyClipboard()
                finally:
                    win32clipboard.CloseClipboard()
                return ActionResult.success("clipboard.clear", detail="Clipboard cleared")
            except Exception as e:
                return ActionResult.failure("clipboard.clear", ActionErrorCode.ACTION_FAILED, detail=str(e))
        return ActionResult.success("clipboard.clear", detail="Clipboard cleared (simulated)")

