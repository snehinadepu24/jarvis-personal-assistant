from __future__ import annotations

import asyncio
import inspect
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

from fastapi import WebSocket

from jarvis.config import Config
from jarvis.api.schemas import CommandType, EventEnvelope, EventType

logger = logging.getLogger("jarvis.api.bridge")


@dataclass
class ActiveTask:
    id: str
    goal: str
    status: str  # pending, running, paused, completed, failed, cancelled
    created_at: str
    task_future: Optional[asyncio.Task] = None
    ctx: Optional[Any] = None
    pending_approval: Optional[asyncio.Future] = None
    current_nonce: Optional[str] = None
    steps: int = 0
    summary: str = ""
    error: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)


class AgentBridge:
    _instance: Optional[AgentBridge] = None

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config.load()
        self.active_websockets: Set[WebSocket] = set()
        self.tasks: Dict[str, ActiveTask] = {}
        self.current_task_id: Optional[str] = None

    @classmethod
    def get_instance(cls, config: Optional[Config] = None) -> AgentBridge:
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance

    async def register_websocket(self, websocket: WebSocket) -> None:
        self.active_websockets.add(websocket)
        logger.info(f"WebSocket client registered. Total active: {len(self.active_websockets)}")
        # Send initial system.ready event
        await self.send_to_client(websocket, EventType.SYSTEM_READY, {
            "status": "ready",
            "active_tasks": len(self.tasks),
            "current_task": self.current_task_id,
        })

    def unregister_websocket(self, websocket: WebSocket) -> None:
        self.active_websockets.discard(websocket)
        logger.info(f"WebSocket client unregistered. Total active: {len(self.active_websockets)}")

    async def broadcast_event(self, event: EventType, data: Dict[str, Any], task_id: Optional[str] = None) -> None:
        envelope = EventEnvelope(
            event=event,
            task_id=task_id,
            data=data,
        )
        payload = envelope.model_dump_json()
        disconnected: Set[WebSocket] = set()
        for ws in self.active_websockets:
            try:
                await ws.send_text(payload)
            except Exception:
                disconnected.add(ws)
        for ws in disconnected:
            self.active_websockets.discard(ws)

    async def send_to_client(self, websocket: WebSocket, event: EventType, data: Dict[str, Any], task_id: Optional[str] = None) -> None:
        envelope = EventEnvelope(
            event=event,
            task_id=task_id,
            data=data,
        )
        try:
            await websocket.send_text(envelope.model_dump_json())
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")

    async def submit_task(
        self,
        goal: str,
        planner_mode: str = "auto",
        engine: str = "state_machine",
        arm: str = "A",
        seed: int = 0,
        task_name: Optional[str] = None,
    ) -> str:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        active = ActiveTask(
            id=task_id,
            goal=goal,
            status="running",
            created_at=created_at,
        )
        self.tasks[task_id] = active
        self.current_task_id = task_id

        await self.broadcast_event(EventType.TASK_ACCEPTED, {
            "task_id": task_id,
            "goal": goal,
            "engine": engine,
        }, task_id=task_id)

        # Launch runner in background
        loop = asyncio.get_running_loop()
        # Create a background task that runs the actual execution coroutine
        task_future = loop.create_task(
            self._execute_task(
                active,
                planner_mode=planner_mode,
                engine=engine,
                arm=arm,
                seed=seed,
                task_name=task_name,
            )
        )
        logger.info(f"[Bridge] Starting task execution: {task_id} goal={goal}")
        active.task_future = task_future
        return task_id

    async def _execute_task(
        self,
        active: ActiveTask,
        planner_mode: str = "auto",
        engine: str = "state_machine",
        arm: str = "A",
        seed: int = 0,
        task_name: str = "task",
    ) -> None:
        task_id = active.id
        goal = active.goal
        cfg = self.config

        fs_root = cfg.data_dir / f"data_{task_id}"
        from jarvis.connectors.files import FilesConnector
        from jarvis.safety.audit import Audit
        from jarvis.safety.gate import ConfirmationGate

        # Check backend
        from jarvis.bench.runner import _use_mock
        
        # Initialize shared components
        snapshot_manager = None
        navigation_strategy = None
        
        if _use_mock(cfg):
            from jarvis.perception.mock_backend import SimulatedDesktop
            from jarvis.actions.mock_executor import MockExecutor
            desktop = SimulatedDesktop(fs_root=fs_root)
            backend = desktop
            executor = MockExecutor(desktop, FilesConnector(fs_root))
        else:
            from jarvis.perception.base import build_backend
            from jarvis.actions.uia_executor import UiaExecutor
            from jarvis.perception.snapshot import get_snapshot_manager
            from jarvis.perception.navigation import create_navigation_strategy
            
            backend = build_backend(cfg)
            
            # Initialize snapshot manager for stale reference detection
            snapshot_manager = get_snapshot_manager()
            
            # Create executor with snapshot manager
            executor = UiaExecutor(backend, FilesConnector(fs_root), snapshot_manager=snapshot_manager)
            
            # Create navigation strategy for complex UI navigation
            navigation_strategy = create_navigation_strategy(backend, executor)

        audit_path = cfg.data_dir / f"audit_{task_id}.db"
        audit = Audit(audit_path)

        async def bridge_confirmer(req) -> bool:
            # Emit approval event to UI
            active.current_nonce = req.nonce
            future = asyncio.get_running_loop().create_future()
            active.pending_approval = future
            await self.broadcast_event(EventType.ACTION_APPROVAL_REQUIRED, {
                "tier": req.tier,
                "nonce": req.nonce,
                "summary": req.summary,
                "window": req.window_title,
                "element": req.element_desc,
                "thought": req.thought,
            }, task_id=task_id)
            try:
                # Wait for user input from UI or timeout
                ans = await asyncio.wait_for(future, timeout=cfg.gate_timeout_s)
                if ans is True or (isinstance(ans, str) and ans.strip() == req.nonce):
                    return req.nonce if req.tier >= 4 else True
                return False
            except asyncio.TimeoutError:
                await self.broadcast_event(EventType.ACTION_FAILED, {
                    "reason": "Confirmation timed out",
                }, task_id=task_id)
                return False
            finally:
                active.pending_approval = None
                active.current_nonce = None

        gate = ConfirmationGate(
            confirmer=bridge_confirmer,
            cancel_window_s=cfg.gate_cancel_window_s,
            timeout_s=cfg.gate_timeout_s,
            speak_summary=False,
        )

        async def event_callback(ev_name: str, ev_data: dict) -> None:
            # Map state machine events to bridge WebSocket events
            ev_type = {
                "task.started": EventType.TASK_STARTED,
                "task.progress": EventType.TASK_PROGRESS,
                "action.started": EventType.ACTION_STARTED,
                "action.completed": EventType.ACTION_COMPLETED,
                "task.completed": EventType.TASK_COMPLETED,
                "task.failed": EventType.TASK_FAILED,
                "task.cancelled": EventType.TASK_CANCELLED,
            }.get(ev_name, EventType.TASK_PROGRESS)
            
            if ev_name == "task.progress":
                active.steps = ev_data.get("step", active.steps)
            elif ev_name == "task.completed":
                active.status = "completed"
                active.summary = ev_data.get("summary", "")
                active.metrics = ev_data.get("metrics", {})
            elif ev_name in ("task.failed", "task.cancelled"):
                active.status = "failed" if ev_name == "task.failed" else "cancelled"
                active.error = ev_data.get("error", "")
                active.metrics = ev_data.get("metrics", {})

            await self.broadcast_event(ev_type, ev_data, task_id=task_id)

        from jarvis.agent.state_machine import AgentContext, run_task
        from jarvis.llm.router import LlmRouter
        from jarvis.llm.gemini import GeminiLLM

        if planner_mode == "scripted":
            from jarvis.agent.skills import ScriptEntry, ScriptedPlanner
            planner = ScriptedPlanner([
                ScriptEntry(thought="Focus Notepad window", action={"type": "open_app", "name": "Notepad", "reason": "focus"}, expect="Notepad open"),
                ScriptEntry(thought="Type note into Notepad", action={"type": "type", "text": "Hello from JARVIS.", "reason": "write text"}, expect="text typed", select={"automation_id": "content"}),
                ScriptEntry(thought="Complete task", action={"type": "done", "summary": "Opened Notepad and wrote greeting", "reason": "complete"}, expect="-"),
            ])
        else:
            # Try to use a pre-defined script for common tasks (faster & more reliable)
            from jarvis.agent.common_scripts import QUICK_LAUNCH, open_notepad_and_type, open_app_fast
            
            script_planner = None
            goal_lower = goal.lower()
            
            # Pattern: "open notepad and write/type X"
            if "notepad" in goal_lower and ("write" in goal_lower or "type" in goal_lower):
                for keyword in ["write", "type"]:
                    if keyword in goal_lower:
                        text = goal_lower.split(keyword)[-1].strip().rstrip('.')
                        script_planner = open_notepad_and_type(text)
                        break
            
            # Pattern: "open/launch [app]"
            if not script_planner:
                for trigger in ["open", "launch", "start"]:
                    if trigger in goal_lower:
                        for app_name, command in QUICK_LAUNCH.items():
                            if app_name in goal_lower:
                                script_planner = open_app_fast(app_name)
                                break
                        if script_planner:
                            break
            
            if script_planner:
                logger.info(f"[Bridge] Using scripted planner for common task pattern")
                planner = script_planner
            else:
                # Fall back to AI planning for complex/unknown tasks
                planner = LlmRouter(GeminiLLM(cfg.planner_model), thinking=cfg.thinking)

        ctx = AgentContext(
            llm=planner,
            backend=backend,
            executor=executor,
            gate=gate,
            audit=audit,
            budgets=cfg.budgets,
            task_name=task_name,
            on_event=event_callback,
            snapshot_manager=snapshot_manager,
            navigation_strategy=navigation_strategy,
        )
        active.ctx = ctx

        try:
            outcome = await run_task(goal, ctx)
            active.status = "completed" if outcome.status == "done" else outcome.status
            active.summary = outcome.summary
            active.error = outcome.error
            active.steps = outcome.steps
            active.metrics = outcome.metrics
        except asyncio.CancelledError:
            active.status = "cancelled"
            await self.broadcast_event(EventType.TASK_CANCELLED, {"reason": "Task cancelled by user"}, task_id=task_id)
        except Exception as e:
            active.status = "failed"
            active.error = str(e)
            await self.broadcast_event(EventType.TASK_FAILED, {"error": str(e)}, task_id=task_id)
        finally:
            if self.current_task_id == task_id:
                self.current_task_id = None

    async def respond_approval(self, task_id: str, nonce: str, approved: bool, reason: str = "") -> bool:
        active = self.tasks.get(task_id)
        if not active or not active.pending_approval:
            return False
        if active.current_nonce and active.current_nonce != nonce:
            return False
        if not active.pending_approval.done():
            active.pending_approval.set_result(approved)
            return True
        return False

    async def cancel_task(self, task_id: str) -> bool:
        active = self.tasks.get(task_id)
        if not active:
            return False
        if active.ctx and hasattr(active.ctx, "cancel"):
            active.ctx.cancel.set()
        if active.task_future and not active.task_future.done():
            active.task_future.cancel()
        active.status = "cancelled"
        await self.broadcast_event(EventType.TASK_CANCELLED, {"reason": "Task cancelled by user"}, task_id=task_id)
        return True

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        active = self.tasks.get(task_id)
        if not active:
            return None
        return {
            "id": active.id,
            "goal": active.goal,
            "status": active.status,
            "steps": active.steps,
            "summary": active.summary,
            "error": active.error,
            "metrics": active.metrics,
            "created_at": active.created_at,
        }

