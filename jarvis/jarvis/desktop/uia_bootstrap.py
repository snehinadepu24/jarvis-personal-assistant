from __future__ import annotations

import sys


def ensure_uia_type_library() -> None:
    """Generate comtypes UI Automation bindings before importing UIA modules."""
    if sys.platform != "win32":
        return
    import comtypes.client

    comtypes.client.GetModule("UIAutomationCore.dll")
    from comtypes.gen import UIAutomationClient  # noqa: F401
