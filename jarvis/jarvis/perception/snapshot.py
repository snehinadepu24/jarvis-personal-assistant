"""
Snapshot-scoped UI element references - Phase 4 Enhancement
Prevents stale element references by binding marks to specific snapshots
"""
from __future__ import annotations

import hashlib
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

@dataclass
class SnapshotReference:
    """A UI element reference bound to a specific snapshot"""
    snapshot_id: str
    mark: int
    element_hash: str  # Hash of element properties for validation
    timestamp: float
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def is_valid(self, current_snapshot_id: str, max_age_seconds: float = 5.0) -> bool:
        """Check if this reference is still valid"""
        # Must be from current snapshot
        if self.snapshot_id != current_snapshot_id:
            return False
        
        # Must not be too old
        age = time.time() - self.timestamp
        if age > max_age_seconds:
            return False
        
        return True


class SnapshotManager:
    """
    Manages screen snapshots and validates element references.
    
    Key features:
    1. Assigns unique IDs to each screen observation
    2. Validates marks are from current snapshot
    3. Detects stale references before action execution
    4. Automatic refresh when references become invalid
    """
    
    def __init__(self, max_age_seconds: float = 5.0):
        self.max_age_seconds = max_age_seconds
        self.current_snapshot_id: Optional[str] = None
        self.snapshots: Dict[str, Any] = {}  # snapshot_id -> Screen
        self.element_cache: Dict[str, SnapshotReference] = {}  # mark -> reference
        self._snapshot_counter = 0
    
    def create_snapshot(self, screen) -> str:
        """
        Create a new snapshot with unique ID.
        
        Args:
            screen: Screen object from perception
            
        Returns:
            Unique snapshot ID
        """
        self._snapshot_counter += 1
        timestamp = time.time()
        
        # Generate unique ID from counter + timestamp + window title
        snapshot_id = hashlib.md5(
            f"{self._snapshot_counter}_{timestamp}_{screen.app}_{screen.window_title}".encode()
        ).hexdigest()[:12]
        
        # Store snapshot
        self.snapshots[snapshot_id] = {
            'screen': screen,
            'timestamp': timestamp,
            'window_title': screen.window_title,
            'app': screen.app,
        }
        
        # Update current
        self.current_snapshot_id = snapshot_id
        
        # Cache element references
        self._cache_elements(snapshot_id, screen)
        
        # Cleanup old snapshots (keep last 5)
        if len(self.snapshots) > 5:
            oldest = sorted(self.snapshots.items(), key=lambda x: x[1]['timestamp'])[0][0]
            del self.snapshots[oldest]
        
        return snapshot_id
    
    def _cache_elements(self, snapshot_id: str, screen):
        """Cache element references with their snapshot ID"""
        for element in screen.elements:
            if not hasattr(element, 'mark'):
                continue
            
            # Create element hash from stable properties
            element_hash = self._hash_element(element)
            
            # Create reference
            ref = SnapshotReference(
                snapshot_id=snapshot_id,
                mark=element.mark,
                element_hash=element_hash,
                timestamp=time.time(),
                properties={
                    'role': getattr(element, 'role', None),
                    'name': getattr(element, 'name', None),
                    'automation_id': getattr(element, 'automation_id', None),
                }
            )
            
            self.element_cache[f"{snapshot_id}_{element.mark}"] = ref
    
    def _hash_element(self, element) -> str:
        """Create stable hash of element properties"""
        # Use role, name, automation_id for identity
        key = f"{getattr(element, 'role', '')}_{getattr(element, 'name', '')}_{getattr(element, 'automation_id', '')}"
        return hashlib.md5(key.encode()).hexdigest()[:8]
    
    def validate_mark(self, mark: int, screen=None) -> tuple[bool, str]:
        """
        Validate that a mark is still valid before use.
        
        Args:
            mark: UI element mark
            screen: Current screen (optional, will check against current snapshot)
            
        Returns:
            (is_valid, reason)
        """
        if self.current_snapshot_id is None:
            return False, "no current snapshot"
        
        # Check if mark exists in current snapshot
        ref_key = f"{self.current_snapshot_id}_{mark}"
        if ref_key not in self.element_cache:
            return False, f"mark {mark} not in current snapshot"
        
        ref = self.element_cache[ref_key]
        
        # Check age
        if not ref.is_valid(self.current_snapshot_id, self.max_age_seconds):
            return False, f"reference expired (age: {time.time() - ref.timestamp:.1f}s)"
        
        # If screen provided, validate element still exists
        if screen:
            element = screen.by_mark(mark)
            if element is None:
                return False, f"mark {mark} no longer on screen"
            
            # Verify element hasn't changed significantly
            current_hash = self._hash_element(element)
            if current_hash != ref.element_hash:
                return False, f"element properties changed"
        
        return True, "valid"
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Any]:
        """Retrieve a stored snapshot by ID"""
        return self.snapshots.get(snapshot_id, {}).get('screen')
    
    def needs_refresh(self) -> bool:
        """Check if current snapshot is stale and needs refresh"""
        if self.current_snapshot_id is None:
            return True
        
        snapshot_data = self.snapshots.get(self.current_snapshot_id)
        if snapshot_data is None:
            return True
        
        age = time.time() - snapshot_data['timestamp']
        return age > self.max_age_seconds
    
    def clear(self):
        """Clear all snapshots"""
        self.snapshots.clear()
        self.element_cache.clear()
        self.current_snapshot_id = None


# Global instance
_manager = None

def get_snapshot_manager() -> SnapshotManager:
    """Get singleton snapshot manager"""
    global _manager
    if _manager is None:
        _manager = SnapshotManager(max_age_seconds=5.0)
    return _manager
