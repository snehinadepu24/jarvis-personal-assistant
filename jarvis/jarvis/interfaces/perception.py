"""
Perception Interface - Stable contract for UI observation

This interface isolates high-level code from perception implementation details.
Agents and API don't need to know about:
- Snapshot managers
- Route selection algorithms
- Confidence thresholds
- Navigation strategies
- Serialization formats

The backend encapsulates all of that complexity.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from jarvis.core.schema import Screen


@dataclass
class ScreenDiff:
    """
    Comparison result between two screens.
    
    This is a value object returned by the backend, not an implementation detail
    that callers need to import from perception.diff module.
    """
    changed: bool
    added: List[str]
    removed: List[str]
    modified: List[str]
    empty: bool
    
    def line(self) -> str:
        """Human-readable summary"""
        if self.empty:
            return "no change"
        parts = []
        if self.added:
            parts.append(f"+{len(self.added)}")
        if self.removed:
            parts.append(f"-{len(self.removed)}")
        if self.modified:
            parts.append(f"~{len(self.modified)}")
        return " ".join(parts) if parts else "no change"


class IPerceptionBackend(ABC):
    """
    Stable interface for perception layer.
    
    High-level modules (agent, API bridge) depend on this interface.
    Low-level modules (UIA backend, mock backend) implement it.
    
    Design principle: The backend owns all perception complexity.
    Callers just say "observe()" and get a Screen back.
    """
    
    @abstractmethod
    async def observe(self) -> Screen:
        """
        Capture current UI state and return structured Screen.
        
        The backend internally decides:
        - Which perception route to use (UIA, OCR, VLM)
        - Whether to escalate routes on failure
        - How to handle stale references
        - When to refresh snapshots
        
        Callers don't need to know any of that.
        
        Returns:
            Screen with elements, window info, snapshot metadata
        """
        pass
    
    @abstractmethod
    def compare(self, before: Optional[Screen], after: Optional[Screen]) -> ScreenDiff:
        """
        Compare two screens and return structured diff.
        
        This replaces direct imports of perception.diff.screen_diff().
        The diff algorithm is an implementation detail.
        
        Args:
            before: Previous screen (can be None)
            after: Current screen (can be None)
            
        Returns:
            ScreenDiff with change summary
        """
        pass
    
    @abstractmethod
    async def wait_idle(self, timeout_ms: int = 5000) -> bool:
        """
        Wait for UI to become idle (no changes for idle_ms).
        
        This encapsulates the polling logic that was scattered across
        perception modules.
        
        Args:
            timeout_ms: Maximum time to wait
            
        Returns:
            True if UI became idle, False if timeout
        """
        pass
    
    @abstractmethod
    def list_windows(self) -> List[dict]:
        """
        List all visible windows.
        
        Returns:
            List of window info dicts with keys: wid, title, class_name
        """
        pass


class IPerceptionBackendFactory(ABC):
    """
    Factory for creating perception backends.
    
    This allows the API bridge to create backends without knowing
    which concrete implementation to instantiate.
    """
    
    @staticmethod
    @abstractmethod
    def create(config: dict) -> IPerceptionBackend:
        """
        Create perception backend based on configuration.
        
        Args:
            config: Configuration dict with backend type, route settings, etc.
            
        Returns:
            Concrete backend implementation
        """
        pass
