from __future__ import annotations

import io

from jarvis.core.schema import Screen
from jarvis.safety.redaction import Redactor


def crop_boxes(rects: list[tuple[int, int, int, int]], padding: int = 4) -> list[tuple[int, int, int, int]]:
    return [(max(0, l - padding), max(0, t - padding), r + padding, b + padding) for l, t, r, b in rects]


def blur_pii_boxes(png_bytes: bytes, screen: Screen) -> bytes:
    from PIL import Image, ImageFilter

    red = Redactor()
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    for e in screen.elements:
        if e.is_password or red.redact(e.value or "")[1] or (e.value and "@" in e.value):
            img.paste(
                img.crop((e.rect.l, e.rect.t, e.rect.r, e.rect.b)).filter(ImageFilter.GaussianBlur(12)),
                (e.rect.l, e.rect.t),
            )
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
