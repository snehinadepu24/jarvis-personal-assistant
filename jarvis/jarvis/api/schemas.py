from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CommandType(str, Enum):
    SYSTEM_INITIALIZE = "system.initialize"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_PING = "system.ping"
    
    TASK_SUBMIT = "task.submit"
    TASK_PAUSE = "task.pause"
    TASK_RESUME = "task.resume"
    TASK_CANCEL = "task.cancel"
    TASK_STATUS = "task.status"
    
    APPROVAL_RESPOND = "approval.respond"
    
    VOICE_START = "voice.start"
    VOICE_STOP = "voice.stop"
    VOICE_CONFIG = "voice.config"


class EventType(str, Enum):
    SYSTEM_READY = "system.ready"
    SYSTEM_ERROR = "system.error"
    SYSTEM_PONG = "system.pong"
    
    TASK_ACCEPTED = "task.accepted"
    TASK_STARTED = "task.started"
    TASK_PLAN_CREATED = "task.plan_created"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_PAUSED = "task.paused"
    TASK_CANCELLED = "task.cancelled"
    
    ACTION_STARTED = "action.started"
    ACTION_APPROVAL_REQUIRED = "action.approval_required"
    ACTION_COMPLETED = "action.completed"
    ACTION_FAILED = "action.failed"
    
    VOICE_LISTENING = "voice.listening"
    VOICE_TRANSCRIPTION = "voice.transcription"
    VOICE_SPEAKING = "voice.speaking"
    VOICE_STATE = "voice.state"


class Envelope(BaseModel):
    version: str = "1.0"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CommandEnvelope(Envelope):
    id: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f"))
    command: CommandType
    data: Dict[str, Any] = Field(default_factory=dict)


class EventEnvelope(Envelope):
    event: EventType
    task_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


class TaskSubmitData(BaseModel):
    goal: str
    planner_mode: str = "auto"
    engine: str = "state_machine"
    arm: str = "A"
    seed: int = 0


class ApprovalResponseData(BaseModel):
    task_id: str
    nonce: str
    approved: bool
    reason: str = ""

