# JARVIS System Architecture

**Product**: Autonomous Adaptive AI Desktop Assistant for Windows 11 & 10  
**Stack**: Tauri 2 (Rust) + React 18 / TypeScript / Tailwind CSS + Python 3.13 (LangGraph / UIA Engine)

---

## 1. High-Level Architectural Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DESKTOP PRESENTATION (React 18 / TS)                  │
│                                                                             │
│   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
│   │   Floating Particles Orb  │         │    Main Dashboard & Monitor   │   │
│   │   (Frameless, Transparent)│         │ (Plan, History, HITL, Config) │   │
│   └─────────────┬─────────────┘         └───────────────┬───────────────┘   │
└─────────────────┼───────────────────────────────────────┼───────────────────┘
                  │                                       │
                  │              IPC / WebSocket          │
                  ▼                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    NATIVE DESKTOP RUNTIME (Tauri 2 / Rust)                  │
│                                                                             │
│ • Window Lifecycle Manager (Orb transparent window, Dashboard normal window)│
│ • Windows System Tray (Menu: Toggle Orb, Open Dashboard, Quit)              │
│ • Global Hotkey Interceptor (`Ctrl + Shift + Space`)                        │
│ • Non-Activating Window Policy (`WS_EX_NOACTIVATE`, `WS_EX_TOOLWINDOW`)      │
│ • Process Supervisor (Launches & monitors Python engine)                    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │
                         Local IPC / WebSocket Protocol
                         (`ws://127.0.0.1:8000/api/ws`)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   JARVIS INTELLIGENCE ENGINE (Python 3.13)                  │
│                                                                             │
│ ┌──────────────────────────┐  ┌─────────────────────────┐  ┌──────────────┐ │
│ │  AgentBridge (FastAPI)   │  │   Perception Cascade    │  │  Executors   │ │
│ │ • WS Broadcast Engine    │  │ Route 1: Connectors     │  │ • UIA Invoker│ │
│ │ • Command Dispatcher     │  │ Route 2: Native UIA     │  │ • Mock Engine│ │
│ │ • HITL Nonce Suspend     │  │ Route 3: OCR / Detector │  │ • Windows Mgr│ │
│ └────────────┬─────────────┘  │ Route 4: Multimodal VLM │  └──────┬───────┘ │
│              │                └────────────┬────────────┘         │         │
│              ▼                             ▼                      ▼         │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │         Supervisor / State Machine / LangGraph Checkpointing            │ │
│ │  • INTERPRET -> ROUTE -> OBSERVE -> DECIDE -> GATE -> ACT -> VERIFY     │ │
│ │  • Thread-Isolated SQLite Checkpointer & Time-Travel Rewind             │ │
│ └────────────────────────────┬────────────────────────────────────────────┘ │
│                              │                                              │
│ ┌────────────────────────────┴────────────────────────────────────────────┐ │
│ │                        Unified 5-Tier Memory                            │ │
│ │ Tier 1: Working (Active turn)        Tier 4: User Profile (Preferences) │ │
│ │ Tier 2: Session (Thread history)     Tier 5: Procedural (Skills YAML)   │ │
│ │ Tier 3: Episodic (SQLite FTS5)                                          │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Directory Boundaries

| Directory | Role | Technologies |
|---|---|---|
| `apps/desktop/src/` | Frontend Presentation | React 18, TypeScript, Tailwind CSS, Canvas2D Fibonacci Particles |
| `apps/desktop/src-tauri/` | Native Windows Host Shell | Tauri 2, Rust, MinGW GCC, Windows API |
| `jarvis/jarvis/` | Autonomous Desktop Core | Python 3.13, LangGraph, Win32 COM, UI Automation |
| `jarvis/jarvis/api/` | Unified Command & Event Bridge | FastAPI, WebSockets, Pydantic v2 |
| `backend/` | Speech Services & Gateway | Moonshine STT, Pocket TTS, openWakeWord, Gemini API |

---

## 3. Core Subsystems

### 3.1. Desktop Windowing & Orb
- **Multi-Window Isolation**: The Orb runs in a dedicated lightweight window with transparency and always-on-top attributes. The Main Dashboard runs in a standard resizable desktop window.
- **Non-Activating Window Behavior**: The Orb window applies `WS_EX_NOACTIVATE` so that clicking or dragging the Orb does not steal focus from the user's active document or IDE.

### 3.2. Perception Cascade (Routes 1–4)
1. **Route 1 (Connectors)**: Direct Win32 COM, Office APIs, or file system manipulations (< 10ms, $0.00).
2. **Route 2 (Native UIA)**: Reads the accessibility tree via UI Automation. Every interactive control receives a snapshot-bound target ref: `@<snapshot_id>:e<mark>` (~150ms).
3. **Route 3 (OCR & Detector)**: Activated if UI controls are custom-drawn or UIA confidence falls below 0.55 (~400ms).
4. **Route 4 (Multimodal VLM)**: Full screenshot analysis by Gemini multimodal vision when visual reasoning is required (~1.5s–3s).

### 3.3. Five-Tier Safety Gate
- **Tier 0-1 (Low)**: Information lookup and non-destructive window navigation. Automatically approved.
- **Tier 2 (Medium)**: File creation, document editing. Automatic notice logged.
- **Tier 3 (High)**: Email drafting, network calls, external modifications. Generates cryptographic action-hash nonce and prompts user confirmation.
- **Tier 4 (Critical)**: File deletion, shell execution, credential operations. Default-deny; requires user confirmation via UI button or typed nonce.

