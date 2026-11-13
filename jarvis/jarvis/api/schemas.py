from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

# Import protocol types - single source of truth
from jarvis.protocol import EventType, CommandType


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

