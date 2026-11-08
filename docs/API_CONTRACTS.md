# JARVIS API Contracts & IPC Protocol

**Version**: 1.0.0  
**Transport**: WebSocket (`ws://127.0.0.1:8000/api/ws`) and REST (`http://127.0.0.1:8000/api`)

---

## 1. WebSocket Protocol Structure

All messages between the desktop frontend (React/Tauri) and the Python intelligence engine follow versioned JSON envelopes.

### Command Envelope (Client -> Server)
```json
{
  "version": "1.0",
  "id": "20261108170000123456",
  "command": "task.submit",
  "data": {
    "goal": "Open Notepad and write Hello from JARVIS.",
    "planner_mode": "auto",
    "engine": "state_machine"
  }
}
```

### Event Envelope (Server -> Client)
```json
{
  "version": "1.0",
  "timestamp": "2026-11-08T11:45:00.000000Z",
  "event": "task.progress",
  "task_id": "task_a1b2c3d4",
  "data": {
    "step": 2,
    "thought": "Type greeting text into Notepad editor",
    "action": {
      "type": "type",
      "text": "Hello from JARVIS.",
      "mark": 3
    },
    "expect": "Editor contains greeting"
  }
}
```

---

## 2. Command Catalog

| Command | Payload Fields | Description |
|---|---|---|
| `task.submit` | `goal: str`, `planner_mode: str`, `engine: str` | Dispatches a new autonomous desktop task to the supervisor planner. |
| `task.pause` | `task_id: str` | Suspends active task execution at the next state transition. |
| `task.resume` | `task_id: str` | Resumes a previously paused task from its SQLite checkpoint. |
| `task.cancel` | `task_id: str` | Cancels active task execution and logs termination to audit trail. |
| `task.status` | `task_id: str` | Queries current task status, step progress, and outcome metrics. |
| `approval.respond` | `task_id: str`, `nonce: str`, `approved: bool`, `reason: str` | Resolves a pending Tier 3 or Tier 4 HITL approval nonce. |
| `system.ping` | `{}` | Heartbeat check; responds with `system.pong`. |

---

## 3. Event Catalog

| Event | Payload Fields | Description |
|---|---|---|
| `system.ready` | `status: str`, `active_tasks: int` | Emitted when WebSocket connection opens and engine is operational. |
| `system.pong` | `status: "pong"` | Heartbeat acknowledgement. |
| `task.accepted` | `task_id: str`, `goal: str`, `engine: str` | Confirms task has been enqueued for execution. |
| `task.started` | `task_id: str`, `goal: str` | Execution loop started (`INTERPRET` state). |
| `task.progress` | `step: int`, `thought: str`, `action: dict`, `expect: str` | Emitted on every step planning decision with model reasoning. |
| `action.started` | `action: dict`, `window: str` | Dispatched immediately before applying action to OS/UIA. |
| `action.approval_required` | `tier: int`, `nonce: str`, `summary: str`, `window: str`, `thought: str` | Emitted when action triggers Risk Tier 3 or 4 gate suspension. |
| `action.completed` | `action: dict`, `result: str`, `ok: bool` | Emitted upon receiving execution receipt from executor. |
| `task.completed` | `status: "completed"`, `summary: str`, `steps: int`, `metrics: dict` | Emitted upon task verification success. |
| `task.failed` | `status: "failed"`, `error: str`, `steps: int` | Emitted upon budget exhaustion or unrecoverable error. |
| `task.cancelled` | `reason: str` | Emitted upon user cancellation. |
| `voice.state` | `state: str` (`idle`, `listening`, `thinking`, `speaking`) | Audio pipeline state transitions. |

---

## 4. REST Endpoints

- `POST /api/task/submit`: Submit a task via HTTP. Returns `{"ok": true, "task_id": "..."}`.
- `GET /api/task/status/{task_id}`: Query task status and execution receipt.
- `POST /api/task/cancel/{task_id}`: Cancel a running task.
- `POST /api/task/approval`: Submit approval response for pending nonce.
- `GET /api/capabilities`: Discover available perception routes, connectors, and memory tiers.
- `POST /api/stt/transcribe`: Upload WAV audio for low-latency STT transcription.
- `POST /api/tts/speech`: Synthesize text to WAV audio using Pocket TTS.

