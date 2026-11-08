from __future__ import annotations

import sys
from typing import Protocol

from jarvis.core.schema import Screen


class PerceptionBackend(Protocol):
    name: str

    async def observe(self, route: int = 2) -> Screen: ...
    async def wait_idle(self, timeout: float = 5.0) -> bool: ...
    def list_windows(self) -> list[dict]: ...
    async def screenshot_bytes(self) -> bytes | None: ...


def build_backend(cfg):
    backend = cfg.backend or "auto"
    if backend == "mock" or (backend == "auto" and sys.platform != "win32"):
        from jarvis.perception.mock_backend import SimulatedDesktop

        return SimulatedDesktop()
    from jarvis.perception.uia import UiaBackend

    return UiaBackend(cfg)
