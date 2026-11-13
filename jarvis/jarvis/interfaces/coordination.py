"""
Coordination Interface - Stable contract for agent orchestration

This interface defines how high-level coordination (API bridge, CLI)
interacts with agent systems without depending on their internals.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Callable, Awaitable, Dict, Any


@dataclass
class TaskOutcome:
    """Result of executing a task"""
    status: str  # "done", "failed", "aborted", "timeout"
    summary: str
    steps: int
    error: str = ""
    metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


class ICoordinator(ABC):
    """
    Stable interface for coordinating agent execution.
    
    This allows the API bridge to run tasks without knowing whether
    it's using state_machine engine, langgraph engine, or some future
    coordinator implementation.
    """
    
    @abstractmethod
    async def execute_task(
        self,
        goal: str,
        context: Optional[Dict[str, Any]] = None,
        on_event: Optional[Callable[[str, Dict], Awaitable[None]]] = None
    ) -> TaskOutcome:
        """
        Execute a task from goal to completion.
        
        Args:
            goal: Natural language goal
            context: Optional context (user preferences, history, etc.)
            on_event: Optional callback for progress events
            
        Returns:
            TaskOutcome with status and metrics
        """
        pass
    
    @abstractmethod
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: Task identifier
            
        Returns:
            True if cancelled, False if not found or already complete
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get coordinator capabilities.
        
        Returns:
            Dict with supported features, limits, configuration
        """
        pass
