"""
JARVIS Protocol Types

Type-safe enums for all protocol messages, events, and states.
These types are shared between Python backend and TypeScript frontend via codegen.
"""

from enum import Enum


# =============================================================================
# EVENT TYPES - Backend → Frontend
# =============================================================================

class EventType(str, Enum):
    """WebSocket events emitted by backend"""
    
    # System Events
    SYSTEM_READY = "system.ready"
    SYSTEM_ERROR = "system.error"
    SYSTEM_PONG = "system.pong"
    
    # Task Lifecycle Events
    TASK_ACCEPTED = "task.accepted"
    TASK_STARTED = "task.started"
    TASK_PLAN_CREATED = "task.plan_created"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_PAUSED = "task.paused"
    TASK_CANCELLED = "task.cancelled"
    
    # Action Events
    ACTION_STARTED = "action.started"
    ACTION_APPROVAL_REQUIRED = "action.approval_required"
    ACTION_COMPLETED = "action.completed"
    ACTION_FAILED = "action.failed"
    
    # Voice Events
    VOICE_LISTENING = "voice.listening"
    VOICE_TRANSCRIPTION = "voice.transcription"
    VOICE_SPEAKING = "voice.speaking"
    VOICE_STATE = "voice.state"


# =============================================================================
# COMMAND TYPES - Frontend → Backend
# =============================================================================

class CommandType(str, Enum):
    """WebSocket commands sent by frontend"""
    
    # System Commands
    SYSTEM_INITIALIZE = "system.initialize"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_PING = "system.ping"
    
    # Task Commands
    TASK_SUBMIT = "task.submit"
    TASK_PAUSE = "task.pause"
    TASK_RESUME = "task.resume"
    TASK_CANCEL = "task.cancel"
    TASK_STATUS = "task.status"
    
    # Approval Commands
    APPROVAL_RESPOND = "approval.respond"
    
    # Voice Commands
    VOICE_START = "voice.start"
    VOICE_STOP = "voice.stop"
    VOICE_CONFIG = "voice.config"


# =============================================================================
# ACTION TYPES - Agent Actions
# =============================================================================

class ActionType(str, Enum):
    """Types of actions the agent can execute"""
    
    # UI Element Interactions
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    CLEAR = "clear"
    TOGGLE = "toggle"
    SELECT_ITEM = "select_item"
    EXPAND = "expand"
    COLLAPSE = "collapse"
    SCROLL = "scroll"
    
    # Keyboard & Window Management
    HOTKEY = "hotkey"
    FOCUS_WINDOW = "focus_window"
    
    # Application Control
    OPEN_APP = "open_app"
    OPEN_URL = "open_url"
    
    # System Commands
    RUN_POWERSHELL = "run_powershell"
    CONNECTOR_CALL = "connector_call"
    
    # Control Flow
    DONE = "done"
    FAIL = "fail"
    WAIT = "wait"
    ASK_USER = "ask_user"


# =============================================================================
# UI STATES
# =============================================================================

class OrbState(str, Enum):
    """Visual states of the floating orb UI"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    EXECUTING = "executing"
    SPEAKING = "speaking"
    ERROR = "error"
    WAITING_APPROVAL = "waiting_approval"


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
