"""
JARVIS Protocol Layer - Single Source of Truth

This module defines all shared types, constants, and contracts between:
- Python backend (jarvis engine)
- TypeScript frontend (desktop app)
- API/IPC layer (WebSocket, REST)

Changes here automatically propagate via code generation (scripts/generate_types.py).
"""

from jarvis.protocol.constants import (
    # API Configuration
    API_HOST,
    API_PORT,
    API_BASE_URL,
    WS_URL,
    
    # Perception Routes
    Route,
    
    # Risk Tiers
    RiskTier,
    TIER_AUTO_APPROVE,
    TIER_REQUIRES_CONFIRMATION,
    TIER_REQUIRES_NONCE,
    
    # Routing Thresholds
    ROUTE_UIA_CONFIDENCE_THRESHOLD,
    ROUTE_FAILURE_ESCALATION_THRESHOLD,
    MAX_RECOVERY_ATTEMPTS,
    
    # Memory Tiers
    MemoryTier,
)

from jarvis.protocol.types import (
    EventType,
    CommandType,
    ActionType,
    OrbState,
    TaskStatus,
)

__all__ = [
    # API
    "API_HOST", "API_PORT", "API_BASE_URL", "WS_URL",
    # Routes
    "Route",
    # Risk
    "RiskTier", "TIER_AUTO_APPROVE", "TIER_REQUIRES_CONFIRMATION", "TIER_REQUIRES_NONCE",
    # Thresholds
    "ROUTE_UIA_CONFIDENCE_THRESHOLD", "ROUTE_FAILURE_ESCALATION_THRESHOLD", "MAX_RECOVERY_ATTEMPTS",
    # Memory
    "MemoryTier",
    # Types
    "EventType", "CommandType", "ActionType", "OrbState", "TaskStatus",
]
