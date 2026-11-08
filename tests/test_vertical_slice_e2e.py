from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Add project roots to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "jarvis"))

import pytest
from jarvis.config import Config
from jarvis.api.bridge import AgentBridge
from jarvis.api.schemas import EventType


def test_vertical_slice_bridge_execution(tmp_path):
    """Verifies that the AgentBridge receives a task, executes it, and emits all lifecycle events."""
    async def _run():
        cfg = Config.load()
        cfg.data_dir = tmp_path
        cfg.backend = "mock"
        cfg.gate_cancel_window_s = 0.0

        bridge = AgentBridge(cfg)

        events_received = []

        class MockWebSocket:
            def __init__(self):
                self.closed = False

            async def send_text(self, text: str):
                import json
                ev = json.loads(text)
                events_received.append(ev)
                ev_type = ev.get("event")
                ev_task = ev.get("task_id")
                data = ev.get("data", {})
                print(f"[WS EVENT RECEIVED] {ev_type} for task {ev_task}", flush=True)
                if ev_type == EventType.ACTION_APPROVAL_REQUIRED.value:
                    nonce = data.get("nonce", "")
                    print(f"[WS AUTO-APPROVING] nonce={nonce}", flush=True)
                    if ev_task:
                        await bridge.respond_approval(ev_task, nonce=nonce, approved=True)

        ws = MockWebSocket()
        await bridge.register_websocket(ws)

        # Submit task: Scripted Notepad goal
        goal = "Open Notepad and write Hello from JARVIS."
        task_id = await bridge.submit_task(
            goal=goal,
            planner_mode="scripted",
            engine="state_machine",
        )

        assert task_id.startswith("task_")

        # Wait for task completion or timeout
        active = bridge.tasks[task_id]
        if active.task_future:
            await asyncio.wait_for(active.task_future, timeout=10.0)

        # Verify task completed
        status = bridge.get_task_status(task_id)
        assert status is not None
        assert status["status"] in ("completed", "done")

        # Verify event stream
        event_names = [e.get("event") for e in events_received]
        assert EventType.SYSTEM_READY.value in event_names
        assert EventType.TASK_ACCEPTED.value in event_names
        assert EventType.TASK_STARTED.value in event_names

        print("\n[E2E TEST PASSED] All events streamed successfully:")
        for ev in events_received:
            print(f"  -> {ev.get('event')}: {ev.get('data', {}).get('status', '') or ev.get('data', {}).get('goal', '')}")

    asyncio.run(_run())


def test_capabilities_endpoint():
    """Verifies that machine-readable capabilities are discoverable for frontend and planners."""
    from jarvis.capabilities import get_system_capabilities
    caps = get_system_capabilities()
    assert caps["version"] == "2.0.0"
    assert "platform" in caps
    assert "perception" in caps
    assert "execution" in caps
    assert "memory_architecture" in caps
    assert len(caps["perception"]["available_routes"]) == 4
