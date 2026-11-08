from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(\+?\d{1,3}[\s.-]?)?(\(?\d{2,4}\)?[\s.-]?)\d{3,4}[\s.-]?\d{3,4}(?!\d)")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")
OTP_RE = re.compile(r"(?<!\d)\d{4,8}(?!\d)")
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")


def luhn_ok(num: str) -> bool:
    digits = [int(d) for d in re.sub(r"\D", "", num)]
    if not 13 <= len(digits) <= 19:
        return False
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


class Redactor:
    def __init__(self):
        self._counters: dict[str, int] = {}

    def _placeholder(self, kind: str) -> str:
        self._counters[kind] = self._counters.get(kind, 0) + 1
        return f"<{kind}_{self._counters[kind]}>"

    def redact(self, text: str) -> tuple[str, dict[str, str]]:
        mapping: dict[str, str] = {}

        def sub(matched: str, kind: str) -> str:
            ph = self._placeholder(kind)
            mapping[ph] = matched
            return ph

        def card_sub(m):
            raw = m.group(0)
            return sub(raw, "CARD") if luhn_ok(raw) else raw

        out = EMAIL_RE.sub(lambda m: sub(m.group(0), "EMAIL"), text)
        out = IBAN_RE.sub(lambda m: sub(m.group(0), "IBAN"), out)
        out = CARD_RE.sub(card_sub, out)
        out = OTP_RE.sub(lambda m: sub(m.group(0), "OTP"), out)
        out = PHONE_RE.sub(lambda m: sub(m.group(0), "PHONE"), out)
        return out, mapping

    def restore(self, text: str, mapping: dict[str, str]) -> str:
        for ph, val in mapping.items():
            text = text.replace(ph, val)
        return text
