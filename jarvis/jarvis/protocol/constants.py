"""
JARVIS Protocol Constants

All magic numbers, thresholds, and configuration defaults.
This is the ONLY file that should contain numeric literals for system behavior.
"""

from enum import IntEnum

# =============================================================================
# API CONFIGURATION
# =============================================================================

API_HOST = "127.0.0.1"
API_PORT = 8000
API_BASE_URL = f"http://{API_HOST}:{API_PORT}/api"
WS_URL = f"ws://{API_HOST}:{API_PORT}/api/ws"


# =============================================================================
# PERCEPTION ROUTES
# =============================================================================

class Route(IntEnum):
    """Perception backend routes - ordered by preference"""
    CONNECTOR = 1      # Direct application API/connector
    UIA = 2            # Windows UI Automation (semantic)
    OCR_DETECTOR = 3   # OCR + visual element detection
    VLM = 4            # Vision-Language Model (multimodal)


# =============================================================================
# RISK TIERS
# =============================================================================

class RiskTier(IntEnum):
    """
    Risk classification for actions - determines approval requirements.
    
    SAFE (0): No confirmation needed (e.g., scroll, focus window)
    LOW (1): Auto-approve if policy allows (e.g., click button)
    MEDIUM (2): Notify user (e.g., toggle checkbox)
    HIGH (3): Explicit confirmation required (e.g., send email)
    CRITICAL (4): Strong confirmation (nonce) or deny (e.g., delete data)
    """
    SAFE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# Tier behavior sets
TIER_AUTO_APPROVE = {RiskTier.SAFE, RiskTier.LOW}
TIER_REQUIRES_CONFIRMATION = {RiskTier.HIGH, RiskTier.CRITICAL}
TIER_REQUIRES_NONCE = {RiskTier.CRITICAL}


# =============================================================================
# ROUTING THRESHOLDS
# =============================================================================

# UIA confidence threshold - below this, escalate to OCR route
ROUTE_UIA_CONFIDENCE_THRESHOLD = 0.55

# Number of route failures before escalating to next route
ROUTE_FAILURE_ESCALATION_THRESHOLD = 2

# Maximum recovery attempts before task fails
MAX_RECOVERY_ATTEMPTS = 3


# =============================================================================
# TIMING CONFIGURATION
# =============================================================================

# Mouse input timing (Windows SendInput requires delays)
MOUSE_CLICK_DELAY_MS = 20
MOUSE_MOVE_DELAY_MS = 20

# UI synchronization waits
MENU_NAVIGATION_WAIT_MS = 300
DIALOG_OPEN_WAIT_MS = 500
WINDOW_FOCUS_WAIT_MS = 50

# Polling intervals
UI_CHANGE_POLL_INTERVAL_MS = 50
UI_CHANGE_TIMEOUT_MS = 2000


# =============================================================================
# RETRY CONFIGURATION
# =============================================================================

# LLM API retries
LLM_MAX_ATTEMPTS_PER_MODEL = 2
LLM_RETRY_DELAY_MS = 500

# Network probes
NETWORK_PROBE_TIMEOUT_MS = 200


# =============================================================================
# MEMORY TIERS
# =============================================================================

class MemoryTier(IntEnum):
    """
    Five-tier memory architecture.
    
    WORKING (1): In-flight scratchpad, diffs, active element refs
    SESSION (2): Short-term thread history, goal stack
    EPISODIC (3): Past task execution history (SQLite + FTS5)
    USER_CONSISTENT (4): Long-term persistent user facts, preferences
    PROCEDURAL (5): Executable skills, workflow shortcuts
    """
    WORKING = 1
    SESSION = 2
    EPISODIC = 3
    USER_CONSISTENT = 4
    PROCEDURAL = 5


# Memory limits
WORKING_MEMORY_MAX_DIFFS = 5
WORKING_MEMORY_MAX_REFS = 20


# =============================================================================
# BUDGET DEFAULTS
# =============================================================================

DEFAULT_MAX_STEPS = 25
DEFAULT_MAX_LLM_CALLS = 40
DEFAULT_MAX_USD = 0.50
DEFAULT_MAX_SECONDS = 300
DEFAULT_MAX_VLM_CALLS = 3
