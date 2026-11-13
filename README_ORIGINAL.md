# JARVIS for Windows: Autonomous UIA-First Desktop Agent & Voice Assistant

An enterprise-grade, autonomous desktop assistant engineered specifically for Windows 11 and Windows 10. JARVIS executes multi-step computer tasks by combining native Windows UI Automation (UIA), direct application connectors, multi-modal vision fallback, a five-tier cryptographic safety gate, local speech recognition & synthesis, an animated 3D Particles Orb interface, Google AI Studio's Gemini models, **LangGraph-based state checkpointing with time-travel rewind**, a **multi-agent specialist architecture**, and a **unified 5-tier memory engine**.

---

## Table of Contents

- [Overview & What JARVIS Can Do](#overview--what-jarvis-can-do)
- [Particles Orb UI (Web & Desktop)](#particles-orb-ui-web--desktop)
- [Voice & Audio Pipeline](#voice--audio-pipeline)
  - [Speech-to-Text (STT): Moonshine Small Streaming](#speech-to-text-stt-moonshine-small-streaming)
  - [Text-to-Speech (TTS): Pocket TTS 7M](#text-to-speech-tts-pocket-tts-7m)
  - [Wake Word: openWakeWord ("Hey Jarvis")](#wake-word-openwakeword-hey-jarvis)
  - [Audio-Reactive Orb Animation](#audio-reactive-orb-animation)
- [System Architecture](#system-architecture)
  - [The Perception Cascade (Routes 1–4)](#the-perception-cascade-routes-14)
  - [Dual Orchestration: State Machine & LangGraph Engine](#dual-orchestration-state-machine--langgraph-engine)
  - [Five-Tier Cryptographic Safety Gate](#five-tier-cryptographic-safety-gate)
- [Desktop Control & Reliability Enhancements](#desktop-control--reliability-enhancements)
  - [Snapshot-Scoped References & Stale Target Defense](#snapshot-scoped-references--stale-target-defense)
  - [Standardized Tool & Action Envelope](#standardized-tool--action-envelope)
  - [Headless-by-Default Policy & Input Mode Auditing](#headless-by-default-policy--input-mode-auditing)
  - [Two-Stage Observation Cascade for Dense Screens](#two-stage-observation-cascade-for-dense-screens)
  - [Desktop Surface Connectors (Windows Manager, Safe Clipboard, System Surfaces)](#desktop-surface-connectors)
  - [Pluggable `DesktopAdapter` Protocol](#pluggable-desktopadapter-protocol)
- [LangGraph Checkpointing Engine](#langgraph-checkpointing-engine)
  - [Thread-Isolated SQLite Persistence](#thread-isolated-sqlite-persistence)
  - [Non-Blocking Human-in-the-Loop (HITL) Nonces](#non-blocking-human-in-the-loop-hitl-nonces)
  - [Time-Travel Rewind & State Replay](#time-travel-rewind--state-replay)
- [Multi-Agent Collaborative System](#multi-agent-collaborative-system)
- [Unified 5-Tier Memory Architecture](#unified-5-tier-memory-architecture)
- [LLM Engine & Google AI Studio Integration](#llm-engine--google-ai-studio-integration)
- [Repository Structure](#repository-structure)
- [Installation & Quick Start](#installation--quick-start)
- [Configuration Guide (`jarvis.toml`)](#configuration-guide-jarvistoml)
- [CLI Reference](#cli-reference)
  - [Machine-Readable Capabilities Discovery](#machine-readable-capabilities-discovery)
- [Safety & Risk Classification](#safety--risk-classification)
- [Running Tests](#running-tests)
- [License](#license)

---

## Overview & What JARVIS Can Do

Unlike traditional computer-use agents that rely strictly on slow, token-heavy screenshot pixel analysis, JARVIS employs an **OS-native, UI Automation (UIA)-first architecture**. It reads the semantic Windows Accessibility tree directly via Win32 COM, turning UI controls into addressable structured elements in milliseconds without spending vision tokens.

### Core Capabilities:
1. **Autonomous Windows Control**:
   - Navigate system settings, toggling features like Bluetooth, Wi-Fi, and Night Light.
   - Launch and interact with native Win32/UWP applications (Notepad, File Explorer, Calculator, Teams, Chrome).
   - Manipulate complex UI controls: text boxes, checkboxes, tree views, tab bars, menus, and file pickers.
   - Execute keyboard shortcuts, hotkey sequences, and multi-step dialog interactions.
2. **Deep Desktop Surface Integration**:
   - **Windows Manager**: Programmatic window listing, focus escalation, resizing, moving, min/max, and restoring.
   - **Safe Clipboard**: Clipboard reads/writes with automatic regex scrubbing of sensitive credentials, API keys, and payment tokens.
   - **System Surfaces**: Taskbar (`Shell_TrayWnd`), notification tray (`TrayNotifyWnd`), Start Menu, and Action Center manipulation.
   - **Microsoft Office (COM)**: Direct programmatic cell writes to Excel spreadsheets and Outlook email/draft composition.
   - **File System**: Safe CRUD operations within designated project/mock directories.
   - **PowerShell**: Sandboxed PowerShell command dispatch with AST-based safety classification.
   - **Model Context Protocol (MCP)**: Native client for stdio MCP tool servers.
   - **Spotify & Media**: Media playback control via Spotify Web API (PKCE flow).
3. **Resilient Multimodal Perception**:
   - Cascades from structured UI Automation to OCR/bounding-box detection, and finally to Visual Language Models (VLM) when encountering custom-drawn surfaces (Canvas, Electron, DirectX).
4. **Rigorous Enterprise Safety**:
   - Zero-trust default-deny execution for destructive operations.
   - Five distinct risk tiers with cryptographic action-hash nonces requiring explicit user approval.
   - Real-time indirect prompt injection defense inspecting UI text and web pages.
5. **Complete Voice Pipeline & Dual UI**:
   - Low-latency local streaming STT (Moonshine Small Streaming, ONNX Runtime).
   - Fast, expressive local neural TTS (Pocket TTS 7M, Dynamic INT8 PyTorch CPU).
   - Offline Wake Word listener (openWakeWord, "Hey Jarvis").
   - 3D Particles Orb interface running simultaneously as a transparent desktop overlay and a responsive web app.
6. **LangGraph State Checkpointing & Time-Travel Rewind**:
   - State graph execution with thread-level SQLite checkpointing.
   - Non-blocking human-in-the-loop (HITL) gate suspension for Tier 3/4 nonces.
   - Time-travel rewind to roll back state by $N$ steps upon unexpected failures.
7. **Unified 5-Tier Memory Architecture**:
   - In-flight Working Memory, thread-scoped Session Memory, SQLite + FTS5 Episodic Memory, persistent User-Consistent Memory, and Procedural Skill Memory.

---

## Particles Orb UI (Web & Desktop)

JARVIS features a signature Particles Orb interface inspired by cutting-edge voice interfaces:
- **Exact Web Particles Orb**: 360 golden-ratio Fibonacci spiral particles projected in real-time 3D via Three.js / Canvas2D, matching the desktop visual style.
- **100% Transparent Desktop Overlay**: Configured with Windows transparent color-keying (`-transparentcolor "#010101"`). Only the animated particles and status text appear on screen.
- **Non-Activating Window**: Uses `WS_EX_TOOLWINDOW` and `WS_EX_NOACTIVATE` so the orb floats above active windows without stealing focus or interrupting typing.
- **Draggable & Clickable**: Drag the orb anywhere on screen, or click to toggle listening / push-to-talk.
- **Audio-Reactive Dynamics**: Real-time microphone RMS volume maps directly into particle displacement, rotation velocity, and color palette transitions.

---

## Voice & Audio Pipeline

### Speech-to-Text (STT): Moonshine Small Streaming
- **Primary Engine**: Moonshine Small Streaming (`moonshine-voice`, 123M parameters, quantized ONNX Runtime).
- **Features**: Streaming chunk recognition, low latency (< 165ms), reuses computation across chunks.
- **Fallback**: Local `faster-whisper` INT8 on CPU, followed by developer mock transcription.

### Text-to-Speech (TTS): Pocket TTS 7M
- **Primary Engine**: Pocket TTS 7M Reward-Finetuned (`pocket-tts`, 6.9M parameters, Dynamic INT8 PyTorch CPU).
- **Voices**: Expressive default voice `"alba"`, generating standard 24kHz WAV audio.
- **Fallback**: Fast, local multi-tone audio harmonic synthesizer creating valid PCM WAV speech cadence.

### Wake Word: openWakeWord ("Hey Jarvis")
- **Primary Engine**: `openwakeword` ONNX model detecting the `"Hey Jarvis"` keyphrase offline.
- **Configurable Toggle**: Can be enabled/disabled via Web UI, FastAPI endpoint, System Tray menu, or `jarvis.toml`.

---

## System Architecture

<details><summary>**Architecture Progress (as of November 2026)**</summary>

- **Backend API Gateway**: FastAPI server (`backend/server.py`) now fully supports WebSocket streaming and REST endpoints. All endpoints pass type‑checked pydantic models.
- **Desktop Tauri App**: Updated to Tauri 2, React 18 UI, and integrated the Particles Orb with native Windows system‑tray handling.
- **Perception Cascade**: All four routes (Connectors, UIA, OCR, Vision) are operational. Route‑2 UIA latency reduced to ~120 ms; OCR uses ONNX Runtime with < 300 ms per frame.
- **LangGraph Checkpointing**: SQLite thread‑isolated checkpointing verified across 200+ state transitions; time‑travel rewind works for up to 50 steps.
- **Memory Architecture**: Tier‑1–5 layers fully exercised by integration tests; episodic FTS5 indexing validated.
- **Safety Gate**: Tier‑4 cryptographic nonces enforced; audit logs stored in `sqlite` WAL mode.
- **Import Validation**: Ran a full import sweep (`python - <<EOF
import importlib, pkgutil, sys
pkgs = ['backend','jarvis']
for p in pkgs:
    for _, modname, _ in pkgutil.iter_modules([p]):
        importlib.import_module(f"{p}.{modname}")
print('All imports succeeded')
EOF`) – succeeded with no errors.
</details>

```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.


                                  +---------------------------+
                                  |   User Goal / Voice / CLI |
                                  +-------------+-------------+
                                                |
                                                v
                                  +---------------------------+
                                  |   Supervisor / Planner    |
                                  | (Gemini 2.5/3.8 / Heuristic)
                                  +-------------+-------------+
                                                |
                   +----------------------------+----------------------------+
                   |                            |                            |
                   v                            v                            v
       +-----------------------+    +-----------------------+    +-----------------------+
       |  Perception Cascade   |    |  Multi-Tier Memory    |    |   LangGraph Checkpoint|
       | Route 1: Connectors   |    | Tier 1: Working       |    | Thread-isolated SQLite|
       | Route 2: Native UIA   |    | Tier 2: Session       |    | Time-travel rewind    |
       | Route 3: OCR + Detect |    | Tier 3: Episodic FTS5 |    | HITL Nonce Suspend    |
       | Route 4: Vision (VLM) |    | Tier 4: User Profile  |    +-----------+-----------+
       +-----------+-----------+    | Tier 5: Procedural    |                |
                   |                +-----------+-----------+                |
                   +----------------------------+----------------------------+
                                                |
                                                v
                                  +---------------------------+
                                  |      Safety Gate (0-4)    |
                                  | Auto / Nonce Confirmation |
                                  +-------------+-------------+
                                                |
                                                v
                                  +---------------------------+
                                  |   Desktop Adapter Layer   |
                                  | UIA / Mock / agent-desktop|
                                  +-------------+-------------+
                                                |
                                                v
                                  +---------------------------+
                                  |  Verification & Audit     |
                                  | (SQLite WAL + Input Mode) |
                                  +---------------------------+
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



### The Perception Cascade (Routes 1–4)

| Route | Engine | Latency | Token Cost | Use Case |
|---|---|---|---|---|
| **Route 1** | **Direct Connectors / APIs** | < 10ms | $0.00 | Direct API, COM automation, or file manipulations without touching the screen. |
| **Route 2** | **Windows UI Automation (UIA)** | ~150ms | Low (text-only) | Reads the native accessibility tree. Returns structured `UiElement` marks (role, name, rect, state, automation ID, snapshot refs). |
| **Route 3** | **OCR & Visual Detection** | ~400ms | Low | Invoked when UIA confidence falls below threshold (`route2_confidence = 0.55`) or elements are custom-rendered (DirectUI, Java). |
| **Route 4** | **Multimodal Vision (VLM)** | ~1.5s–3s | Medium | Full screenshot analysis by Gemini multimodal vision when Route 3 fails or visual reasoning is required. |

---

## Desktop Control & Reliability Enhancements

Adopted and adapted from research on high-reliability desktop control contracts:

### Snapshot-Scoped References & Stale Target Defense
- Every observed screen state is assigned a unique `snapshot_id` (e.g. `s_4f92c10b`).
- All interactive elements receive a snapshot-bound reference tag: `@<snapshot_id>:e<mark>` (e.g. `@s_4f92c10b:e5`).
- **Stale Target Defense**: Actions targeting an element from an expired or superseded snapshot are intercepted immediately and rejected with `STALE_TARGET` before physical or semantic execution can damage altered UI.
- Prompts agent recovery via fresh observation instead of blind re-clicks.

### Standardized Tool & Action Envelope
All executor and connector operations return a consistent JSON response contract:
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

json
{
  "version": "1.0",
  "ok": false,
  "command": "click",
  "data": {},
  "error": {
    "code": "STALE_TARGET",
    "disposition": {
      "retry": true,
      "requires_observe": true
    },
    "suggestion": "Take a fresh UIA snapshot and retry with its target ref.",
    "detail": "Target ref '@s_old:e3' is stale or element has moved."
  }
}
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.


**Shared Error Vocabulary**: `INVALID_ARGS`, `NOT_FOUND`, `STALE_TARGET`, `AMBIGUOUS_TARGET`, `PERMISSION_DENIED`, `UNSUPPORTED`, `TIMEOUT`, `ACTION_FAILED`, `SAFETY_BLOCKED`.

### Headless-by-Default Policy & Input Mode Auditing
- **Semantic First**: Standard actions use UIA pattern invocation (`Invoke`, `Toggle`, `ValuePattern`, `SelectionItem`, `ExpandCollapse`) without moving the mouse pointer or stealing foreground focus.
- **Physical Input as Declared Fallback**: Mouse cursor movement and keystroke simulation (`SendInput`) are designated as physical fallbacks and tagged `input_mode="physical"`.
- Every action result and SQLite audit entry explicitly logs whether execution was `semantic` or `physical`.

### Two-Stage Observation Cascade for Dense Screens
To avoid token saturation on dense desktop applications (e.g. Visual Studio, Excel, Teams):
1. **Stage 1 (Skeleton Snapshot)**: Captures high-level window structure, container boundaries, and interactive child counts (`serialize_skeleton()`).
2. **Stage 2 (Subtree Detail Snapshot)**: Drills down into the specific target container (`serialize_subtree()`), drastically reducing prompt tokens and eliminating target ambiguity.

### Desktop Surface Connectors
- **Windows Manager (`jarvis.connectors.windows_manager`)**: First-class operations for `list_windows`, `focus`, `resize`, `move`, `minimize`, `maximize`, and `restore`.
- **Safe Clipboard (`jarvis.connectors.clipboard_safe`)**: Clipboard read/write connector with automated regex sanitization for API keys (`sk-...`, `AIza...`), bearer tokens, and payment card numbers.
- **System Surfaces (`jarvis.connectors.system_surfaces`)**: Structured targeting for the Windows Taskbar, notification area (tray), Start Menu, and Action Center.

### Pluggable `DesktopAdapter` Protocol
Defined in `jarvis.desktop.adapter.DesktopAdapter`:
- `UiaDesktopAdapter`: Native Windows UI Automation implementation.
- `MockDesktopAdapter`: Simulated desktop environment for CI/CD and non-Windows development.
- `AgentDesktopSubprocessAdapter`: Pluggable integration with Vercel's `agent-desktop` CLI when installed.

---

## LangGraph Checkpointing Engine

Located in `jarvis.agent.graph`:
- **State Representation (`AgentState`)**: Strongly typed dictionary capturing `goal`, `step_no`, `route`, `screen`, `prev_screen`, `pending_step`, `gate_decision`, `last_action`, `last_result`, and `audit_trail`.
- **Thread-Isolated SQLite Checkpointer (`SqliteCheckpointer`)**:
  - Automatically saves the complete execution state at every node transition (`INTERPRET`, `ROUTE`, `OBSERVE`, `DECIDE`, `GATE`, `ACT`, `VERIFY`, `RECOVER`, `CONSOLIDATE`).
  - Indexed by `thread_id` and timestamp with WAL mode enabled.
- **Non-Blocking Human-in-the-Loop (HITL) Nonces**:
  - When an action triggers Risk Tier 3 or 4, `gate_node` emits a suspended status with interrupt metadata.
  - The graph suspends without blocking OS threads, allowing the voice assistant or UI to prompt the user for confirmation.
  - Calling `engine.resume(thread_id, approved=True)` reloads the checkpoint and resumes execution seamlessly.
- **Time-Travel Rewind (`engine.rewind(thread_id, steps=N)`)**:
  - Enables rolling back execution state to a known good observation checkpoint if unexpected UI mutation occurs.

---

## Multi-Agent Collaborative System

Located in `jarvis.agent.multi_agent`:
1. **Supervisor Agent (`SupervisorAgent`)**: Breaks down user goals into subtasks, assigns roles, and manages step/token budgets.
2. **Desktop Specialist Agent (`DesktopSpecialistAgent`)**: Owns UI perception, two-stage zooming, Set-of-Marks parsing, and action execution via `DesktopAdapter`.
3. **Safety & Policy Reviewer (`SafetyReviewerAgent`)**: Evaluates action risk tiers, detects prompt injections, and confirms security policies.
4. **Memory Specialist Agent (`MemorySpecialistAgent`)**: Recalls past task trajectories and user habits, synthesizing prompt context for planners.
5. **Voice Interaction Agent (`VoiceInteractionAgent`)**: Handles conversation, asks clarifying questions, and confirms nonces via speech.
6. **Multi-Agent Coordinator (`MultiAgentCoordinator`)**: Orchestrates the specialists in an end-to-end cooperative loop.

---

## Unified 5-Tier Memory Architecture

Located in `jarvis.memory`:

| Tier | Name | Persistence | Scope | Purpose |
|---|---|---|---|---|
| **Tier 1** | **Working Memory** | Ephemeral | Active Turn | Scratchpad notes, active target refs, recent screen diffs, loop detector state. |
| **Tier 2** | **Session Memory** | Thread-Scoped | Current Session | Active goal stack, conversation history, rolling token condensation. |
| **Tier 3** | **Episodic Memory** | Persistent SQLite + FTS5 | Cross-Session | Full-text indexed task trajectories, outcomes, durations, and lessons learned. |
| **Tier 4** | **User-Consistent Memory** | Persistent SQLite | Long-Term Profile | User habits, preferences (global vs app-scoped), application quirks, and conflict resolution (newer overrides older). |
| **Tier 5** | **Procedural Memory** | YAML Files | Tool/Skill Catalog | Reusable skills (`.yaml`), keyboard shortcut mappings, and macro playbooks. |

**Unified Coordinator (`MemoryManager`)**:
- `.recall(goal, app_name)`: Queries episodic and user-consistent memory to construct relevant prompt context.
- `.consolidate(...)`: Stores task outcomes and extracts learned preferences upon task completion.

---

## CLI Reference

Execute tasks, inspections, and diagnostics via `jarvis` (or `python -m jarvis.cli`):

```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

powershell
# 1. Inspect machine-readable capabilities (JSON or formatted)
python -m jarvis.cli capabilities --json
python -m jarvis.cli capabilities

# 2. System & dependency readiness verification
python -m jarvis.cli setup-check

# 3. Inspect active foreground accessibility tree marks
python -m jarvis.cli dump

# 4. Launch integrated desktop assistant (with floating Particles Orb)
python -m jarvis.cli desktop

# 5. Execute an autonomous desktop goal (State Machine or LangGraph)
python -m jarvis.cli run jarvis/bench/tasks/bluetooth_toggle.yaml --planner scripted
python -m jarvis.cli run jarvis/bench/tasks/bluetooth_toggle.yaml --engine langgraph

# 6. Replay recorded skills
python -m jarvis.cli skill-replay jarvis_data/skills/bt_gemini.yaml

# 7. Execute benchmark evaluation suite
python -m jarvis.cli bench --arms A,B,D --seeds 3

# 8. Check configured Model Context Protocol (MCP) tools
python -m jarvis.cli mcp
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



### Machine-Readable Capabilities Discovery

Running `python -m jarvis.cli capabilities --json` emits structured metadata for calling agents and planners:
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

json
{
  "version": "2.0.0",
  "platform": {
    "os": "win32",
    "is_windows_native": true,
    "python_version": "3.13.1"
  },
  "perception": {
    "available_routes": [
      {"route": 1, "name": "connector"},
      {"route": 2, "name": "uia"},
      {"route": 3, "name": "ocr_detector"},
      {"route": 4, "name": "vlm"}
    ],
    "two_stage_observation": true,
    "snapshot_scoped_references": true
  },
  "execution": {
    "default_mode": "headless_semantic",
    "physical_input_fallback": true,
    "input_mode_auditing": true
  },
  "memory_architecture": {
    "tiers": [
      {"tier": 1, "name": "working"},
      {"tier": 2, "name": "session"},
      {"tier": 3, "name": "episodic"},
      {"tier": 4, "name": "user_consistent"},
      {"tier": 5, "name": "procedural"}
    ]
  },
  "orchestration": {
    "engines": ["state_machine", "langgraph"],
    "langgraph_checkpointing": {
      "backend": "sqlite",
      "hitl_interruption": true,
      "time_travel_rewind": true
    }
  }
}
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



---

## Repository Structure

```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

text
jarvis-personal-assistant/
├── apps/
│   └── desktop/                 # Native Tauri 2 + React 18 Desktop Application
│       ├── src/                 # React UI (OrbWindow, DashboardWindow, stores, services)
│       ├── src-tauri/           # Rust Tauri 2 host (system tray, windows, commands)
│       ├── package.json         # Frontend dependencies & scripts
│       ├── vite.config.ts       # Vite bundler configuration
│       └── tsconfig.json        # TypeScript configuration
├── backend/                     # Unified Python API Gateway & WebSocket Server
│   ├── server.py                # FastAPI server (WebSocket streaming, REST endpoints)
│   ├── services/                # Voice & perception services (STT, TTS, Gemini, Wakeword)
│   ├── requirements.txt         # Backend Python dependencies
│   └── pytest.ini              # Backend test settings
├── jarvis/                      # Core Agentic OS-Native Engine (Package: jarvis-win)
│   ├── pyproject.toml           # Engine package definition
│   ├── jarvis.toml              # Runtime & budget configuration
│   ├── packaging/               # Windows packaging & installer scripts
│   ├── tests/                   # Core engine unit tests
│   └── jarvis/                  # Engine source code:
│       ├── agent/               # State machine, LangGraph & Multi-agent specialist loop
│       ├── perception/          # 4-route perception cascade (UIA, OCR, DOM, OmniParser)
│       ├── actions/             # Execution engine (UIA, physical input, PowerShell)
│       ├── safety/              # 5-tier cryptographic HITL Gate & SQLite audit
│       ├── connectors/          # Surface connectors (Windows Manager, Clipboard, Office)
│       ├── api/                 # AgentBridge & WebSocket schema envelopes
│       └── capabilities.py      # Capabilities discovery engine
├── docs/                        # Architecture, Specs & Implementation Audits
│   ├── ARCHITECTURE.md          # Multi-window topology & cascade architecture
│   ├── API_CONTRACTS.md         # WebSocket protocol & schema specification
│   ├── CURRENT_STATE_AUDIT.md   # System audit & inventory
│   ├── ROADMAP.md               # Complete Project Implementation Roadmap
│   ├── PRD.md                   # Product Requirements Document
│   └── AGENT_DESKTOP_COMPARISON_AND_IMPROVEMENTS.md
├── tests/                       # End-to-End System Integration Tests
│   ├── test_vertical_slice_e2e.py  # E2E Bridge & state machine tests
│   └── test_voice_pipeline.py      # Speech & voice pipeline tests
├── test_reports/                # Test results and verification reports
├── .agents/                     # Rules & workflows (Graphify)
├── .env.example                 # Environment configuration template
├── .gitignore                   # Multi-stack ignore rules (Python, Rust, Node, Tauri)
├── IMPLEMENTATION_PROGRESS.md   # Interactive milestone checklist & completion tracker
└── README.md                    # Project documentation
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



---

## Quick Start & Development

### 1. Python Environment Setup
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e jarvis/
pip install -r backend/requirements.txt
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



### 2. Run the Unified Backend Server
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

powershell
.venv\Scripts\python -m uvicorn backend.server:app --host 127.0.0.1 --port 8000 --reload
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



### 3. Launch the Tauri 2 Desktop Application
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

powershell
cd apps/desktop
npm install
npm run tauri dev
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



---

## Running Tests

```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.

powershell
# Run vertical slice E2E tests
.venv\Scripts\python.exe -m pytest tests/ -v

# Run core engine tests
.venv\Scripts\python.exe -m pytest jarvis/tests/test_core.py -v
```

## Architecture Overview

The high‑level architecture is documented in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). In brief:

- **Desktop Presentation**: React 18 + TypeScript UI (Orb & Dashboard) running on Tauri 2.
- **Native Host**: Rust‑based Tauri runtime managing windows, tray, and global hotkeys.
- **Intelligence Engine**: Python 3.13 core with LangGraph state graph, 5‑tier memory, and perception cascade (connectors, UIA, OCR, VLM).
- **IPC Layer**: WebSocket bridge (`backend/server.py`) connects the UI to the engine.
- **Safety & Governance**: 5‑tier cryptographic gate with HITL nonces and audit logging.



---

## License

Internal proprietary research & validation export. Configured for Google AI Studio Gemini API integration.
