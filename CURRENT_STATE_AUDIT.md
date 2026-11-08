# JARVIS — Current State Audit & System Inventory

**Date**: 2026-11-08  
**Target Architecture**: Windows-First Autonomous Assistant (Tauri 2 + Python LangGraph/UIA Engine + Particles Orb)

---

## 1. Executive Summary

This audit assesses the state of the codebase prior to the Milestone 1 execution, identifying existing working modules, partially connected services, and architectural gaps.

```
                              EXISTING REPOSITORY ASSETS
 ┌─────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────────────┐
 │        jarvis/          │   │         backend/         │   │        frontend/        │
 │ • UIA Perception (1-4)  │   │ • Moonshine STT (ONNX)   │   │ • React (CRA/craco)     │
 │ • Action Executors      │   │ • Pocket TTS (PyTorch)   │   │ • 3D Particles Orb      │
 │ • LangGraph Checkpoints │   │ • openWakeWord           │   │ • Voice Settings UI     │
 │ • 5-Tier Memory         │   │ • FastAPI HTTP server    │   │ (Runs only in browser)  │
 │ • Safety Gate (Tiers0-4)│   │ • Gemini AI Service      │   │                         │
 └───────────┬─────────────┘   └────────────┬─────────────┘   └────────────┬────────────┘
             │                              │                              │
             └─────────────── X ────────────┴─────────────── X ────────────┘
                           [Disconnected Prior to Milestone 1]
```

---

## 2. Feature & Component Matrix

| Subsystem | Location | Current Implementation Status | Evaluation & Action Required |
|---|---|---|---|
| **UI Automation (UIA)** | `jarvis/perception/uia.py`, `actions/uia_executor.py` | **Working** | Robust Win32 COM & UI Automation tree extraction with Set-of-Marks and snapshot-scoped refs (`@snapshot:eId`). |
| **Perception Cascade** | `jarvis/perception/` (`router.py`, `ocr.py`, `vision.py`) | **Working** | Four routes (Connectors -> UIA -> OCR/Detector -> Multimodal Gemini VLM). |
| **Agent Orchestration** | `jarvis/agent/state_machine.py`, `jarvis/agent/graph/` | **Working** | Dual-engine: Async state machine and LangGraph with SQLite checkpointing and HITL nonce interrupts. |
| **5-Tier Memory** | `jarvis/memory/` | **Working** | Working, Session, Episodic (SQLite FTS5), User Profile, and Procedural Skills. |
| **Safety & Policy Gate** | `jarvis/safety/` | **Working** | Tiers 0-4 risk classifier, cryptographic action hash nonces, regex redaction, prompt injection defense, SQLite audit trail. |
| **Speech-to-Text (STT)** | `backend/services/stt_service.py` | **Working** | Moonshine Small Streaming ONNX runtime (quantized) with Whisper and mock fallbacks. |
| **Text-to-Speech (TTS)** | `backend/services/tts_service.py` | **Working** | Pocket TTS 7M (Dynamic INT8 PyTorch) with harmonic synthesizer fallback. |
| **Wake Word Detection** | `backend/services/wakeword_service.py` | **Working** | `openwakeword` ONNX detection for "Hey Jarvis". |
| **HTTP API Server** | `backend/server.py` | **Partial** | Exposes STT/TTS and chat endpoints, but **not connected** to `jarvis` agent execution or state machine. |
| **Backend/Frontend IPC** | `backend/server.py` <-> `frontend/src/` | **Partial** | Basic REST endpoints and simple WebSocket stub; lacks structured command/event protocol. |
| **Desktop Shell / UI** | `frontend/src/`, `jarvis/ui/` | **Partial** | React app renders Three.js Particles Orb in browser. `jarvis/ui/overlay.py` has an obsolete Tkinter prototype. **Missing native Tauri 2 desktop shell**. |
| **Windows Packaging** | Root | **Missing** | No PyInstaller spec or Tauri installer bundle yet configured. |

---

## 3. Critical Integration Gaps to Resolve in Milestone 1

1. **Bridge Backend to JARVIS Engine**:
   - `backend/server.py` must import and initialize `jarvis` agent execution (`jarvis.agent.state_machine` and `jarvis.config.Config`).
   - Implement standard command contracts (`task.submit`, `task.pause`, `task.resume`, `task.cancel`, `approval.respond`) and real-time WebSocket event streaming.
2. **Scaffold Tauri 2 Native Desktop Shell (`apps/desktop`)**:
   - Transition from browser-only React to native Windows windows.
   - Transparent, always-on-top, non-activating floating Particles Orb (`WS_EX_NOACTIVATE`).
   - Native System Tray with status indicators and global shortcut (`Ctrl+Shift+Space`).
3. **Validate End-to-End Vertical Slice**:
   - Deliver the benchmark: `"Open Notepad and write Hello from JARVIS"`.

