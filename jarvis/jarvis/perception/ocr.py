from __future__ import annotations

import sys

if sys.platform != "win32":
    raise ImportError("ocr.py is Windows-only (Windows.Media.Ocr via PyWinRT); keep Tesseract/PaddleOCR as backup")

import mss


async def ocr_region(l: int, t: int, r: int, b: int) -> list[dict]:
    from winrt.windows.graphics.imaging import BitmapAlphaMode, BitmapPixelFormat, SoftwareBitmap
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage.streams import DataWriter

    with mss.mss() as s:
        img = s.grab({"left": l, "top": t, "width": r - l, "height": b - t})
    w = DataWriter()
    w.write_bytes(bytes(img.bgra))
    sb = SoftwareBitmap.create_copy_from_buffer(
        w.detach_buffer(), BitmapPixelFormat.BGRA8, img.width, img.height, BitmapAlphaMode.PREMULTIPLIED
    )
    res = await OcrEngine.try_create_from_user_profile_languages().recognize_async(sb)
    return [
        {
            "text": wd.text,
            "rect": (
                l + int(wd.bounding_rect.x),
                t + int(wd.bounding_rect.y),
                l + int(wd.bounding_rect.x + wd.bounding_rect.width),
                t + int(wd.bounding_rect.y + wd.bounding_rect.height),
            ),
        }
        for line in res.lines
        for wd in line.words
    ]
