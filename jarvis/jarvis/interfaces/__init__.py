"""
JARVIS Interfaces - Dependency Inversion Layer

This module defines stable interfaces that high-level modules (agent, API)
depend on, while low-level modules (perception, execution) implement them.

Benefits:
- High-level modules don't depend on implementation details
- Low-level modules can change without affecting callers
- Easier testing (mock implementations)
- Clear architectural boundaries
"""

from jarvis.interfaces.perception import IPerceptionBackend, ScreenDiff
from jarvis.interfaces.execution import IActionExecutor, ActionResult
from jarvis.interfaces.coordination import ICoordinator

__all__ = [
    "IPerceptionBackend",
    "ScreenDiff",
    "IActionExecutor",
    "ActionResult",
    "ICoordinator",
]
