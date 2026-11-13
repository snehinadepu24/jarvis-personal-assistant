"""
Execution Interface - Stable contract for action execution

This interface isolates high-level code from executor implementation details.
Agents and API don't need to know about:
- Snapshot managers
- Navigation strategies
- UIA pattern selection
- Fallback mechanisms (semantic → physical input)
- Platform-specific primitives

The executor encapsulates all of that complexity.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict
from jarvis.core.schema import Step, Screen


class ActionErrorCode(str, Enum):
    """Standard error codes for action failures"""
    SUCCESS = "success"
    ELEMENT_NOT_FOUND = "element_not_found"
    STALE_REFERENCE = "stale_reference"
    NOT_SUPPORTED = "not_supported"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    ACTION_FAILED = "action_failed"


@dataclass
class ActionResult:
    """
    Result of executing an action.
    
    This is a value object that represents execution outcome,
    not tied to any specific executor implementation.
    """
    ok: bool
    command: str
    error_code: Optional[ActionErrorCode] = None
    detail: str = ""
    artifact: Optional[Dict[str, Any]] = None
    input_mode: str = "semantic"  # "semantic" or "physical"
    
    @staticmethod
    def success(command: str, detail: str = "", artifact: Optional[Dict] = None, input_mode: str = "semantic") -> 'ActionResult':
        """Create success result"""
        return ActionResult(
            ok=True,
            command=command,
            error_code=ActionErrorCode.SUCCESS,
            detail=detail,
            artifact=artifact,
            input_mode=input_mode
        )
    
    @staticmethod
    def failure(command: str, error_code: ActionErrorCode, detail: str = "", artifact: Optional[Dict] = None, input_mode: str = "semantic") -> 'ActionResult':
        """Create failure result"""
        return ActionResult(
            ok=False,
            command=command,
            error_code=error_code,
            detail=detail,
            artifact=artifact,
            input_mode=input_mode
        )
    
    @staticmethod
    def stale_target(command: str, ref: str, snapshot_id: str) -> 'ActionResult':
        """Create stale reference error"""
        return ActionResult(
            ok=False,
            command=command,
            error_code=ActionErrorCode.STALE_REFERENCE,
            detail=f"Target {ref} from snapshot {snapshot_id} is stale"
        )


class IActionExecutor(ABC):
    """
    Stable interface for action execution.
    
    High-level modules (agent, API bridge) depend on this interface.
    Low-level modules (UIA executor, mock executor) implement it.
    
    Design principle: The executor owns all execution complexity.
    Callers just say "execute(step, screen)" and get a result back.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Executor implementation name (e.g., 'uia-executor', 'mock-executor')"""
        pass
    
    @abstractmethod
    async def execute(self, step: Step, screen: Screen) -> ActionResult:
        """
        Execute a validated action against the current screen.
        
        The executor internally handles:
        - Resolving element references
        - Validating snapshot freshness
        - Choosing between semantic and physical input
        - Fallback strategies when patterns fail
        - Platform-specific details
        
        Callers don't need to know any of that.
        
        Args:
            step: Step with action to execute
            screen: Current screen snapshot (for element resolution)
            
        Returns:
            ActionResult indicating success/failure and execution method
        """
        pass


class IActionExecutorFactory(ABC):
    """
    Factory for creating action executors.
    
    This allows the API bridge to create executors without knowing
    which concrete implementation to instantiate.
    """
    
    @staticmethod
    @abstractmethod
    def create(backend: Any, config: dict) -> IActionExecutor:
        """
        Create action executor based on configuration.
        
        Args:
            backend: Perception backend (for element lookups)
            config: Configuration dict with executor type, connectors, etc.
            
        Returns:
            Concrete executor implementation
        """
        pass
