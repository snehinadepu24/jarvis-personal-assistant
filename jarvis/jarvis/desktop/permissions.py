from __future__ import annotations

import os
import sys
import webbrowser
from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionStatus:
    microphone: bool
    uia: bool
    wakeword: bool
    details: tuple[str, ...] = ()

    @property
    def ready(self) -> bool:
        return self.microphone and self.uia and self.wakeword


def check_permissions(*, wakeword_required: bool) -> PermissionStatus:
    if sys.platform != "win32":
        return PermissionStatus(False, False, False, ("Windows is required for desktop mode.",))

    details: list[str] = []
    microphone = True
    try:
        import sounddevice as sd

        sd.query_devices(kind="input")
    except Exception as error:
        microphone = False
        details.append(f"Microphone unavailable: {error}")

    uia = True
    try:
        from jarvis.desktop.uia_bootstrap import ensure_uia_type_library

        ensure_uia_type_library()
        import win32gui  # noqa: F401
        import uiautomation  # noqa: F401
    except ImportError as error:
        uia = False
        details.append(f"Windows UI Automation dependencies unavailable: {error}")

    wakeword = True
    if wakeword_required:
        try:
            from jarvis.voice.wakeword import WakeWord

            detector = WakeWord(enabled=False)
            wakeword = detector._model is not None
            detector.stop()
            if not wakeword:
                details.append("Wake-word model is unavailable. Install the hey_jarvis ONNX model.")
        except Exception as error:
            wakeword = False
            details.append(f"Wake-word initialization failed: {error}")

    return PermissionStatus(microphone, uia, wakeword, tuple(details))


def open_microphone_settings() -> None:
    if sys.platform == "win32":
        os.startfile("ms-settings:privacy-microphone")
    else:
        webbrowser.open("https://support.microsoft.com/windows")


def open_accessibility_settings() -> None:
    if sys.platform == "win32":
        os.startfile("ms-settings:easeofaccess")
