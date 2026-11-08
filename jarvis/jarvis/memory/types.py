from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class Fact:
    key: str
    value: str
    category: str = "general"
    confidence: float = 1.0
    ts: float = field(default_factory=time.time)


@dataclass
class UserPreference:
    key: str
    value: Any
    scope: Literal["global", "app", "task"] = "global"
    app_name: str = ""
    ts: float = field(default_factory=time.time)
    overridden_at: float | None = None


@dataclass
class EpisodicRecord:
    task_id: str
    goal: str
    steps_json: str
    status: Literal["done", "failed", "aborted"]
    summary: str = ""
    error: str = ""
    duration_s: float = 0.0
    recovery_count: int = 0
    created_at: float = field(default_factory=time.time)


@dataclass
class SessionCheckpoint:
    thread_id: str
    step_no: int
    goal: str
    active_window: str
    last_action: str
    last_result: str
    metrics: dict = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


@dataclass
class WorkingMemoryState:
    active_refs: list[str] = field(default_factory=list)
    recent_diffs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    loop_count: int = 0

