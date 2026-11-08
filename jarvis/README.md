# JARVIS for Windows: Desktop Agent

UIA-first desktop agent: one Python process in the interactive session, three threads
(UIA MTA worker / asyncio agent loop / audio), semantic-first perception cascade
connector -> UIA Set-of-Marks -> OCR/detector -> VLM, tiered safety gate, append-only audit,
LangGraph-based state checkpointing with time-travel rewind, multi-agent specialist architecture,
unified 5-tier memory engine, and an interactive, transparent floating Particles Orb overlay.

Implements the v2.0 build document. On Windows it runs the real UIA stack;
on non-Windows hosts the same agent core runs against a faithful simulated desktop
(`jarvis.perception.mock_backend`) so everything except the Win32 layer is verifiable anywhere.

---

## Layout & Architecture

| Path | Contents |
|---|---|
| `jarvis/core/` | `schema.py` (Screen, snapshot refs `@sid:e<mark>`, standard `ActionEnvelope`, `ActionError`, Union Action, Step), `prompts.py`, `skills_format.py` |
| `jarvis/perception/` | `base.py` (PerceptionBackend protocol), `serialize.py` (two-stage observation: `serialize_skeleton` and `serialize_subtree`), `diff.py`, `router.py`, `uia.py` (MTA thread + cache request + snapshot IDs), `events.py`, `ocr.py`, `mock_backend.py` |
| `jarvis/actions/` | `base.py` (`ActionResult` with envelope, structured errors, and `input_mode`), `mock_executor.py` (stale ref rejection), `uia_executor.py` (headless semantic patterns + SendInput fallback), `window.py`, `verify.py` |
| `jarvis/agent/` | `state_machine.py` (classic state machine loop), `budgets.py`, `loop_detect.py`, `memory.py`, `skills.py` |
| `jarvis/agent/graph/` | LangGraph checkpointing engine: `state.py`, `checkpointer.py` (SQLite checkpointer with rewind), `nodes.py`, `engine.py` (HITL suspension on Tier 3/4 nonces) |
| `jarvis/agent/multi_agent/` | Multi-agent specialist architecture: `supervisor.py`, `desktop_specialist.py`, `safety_reviewer.py`, `memory_specialist.py`, `voice_interaction.py`, `coordinator.py` |
| `jarvis/memory/` | Unified 5-tier memory: `working.py` (Tier 1), `session.py` (Tier 2), `episodic.py` (Tier 3 SQLite + FTS5), `user_consistent.py` (Tier 4 persistent profile/habits), `procedural.py` (Tier 5 skills/shortcuts), `manager.py` |
| `jarvis/llm/` | `gemini.py` (Google AI Studio Gemini API client), `local.py`, `openai_compat.py`, `router.py`, `costs.py` |
| `jarvis/safety/` | `risk.py` (tiers 0-4), `gate.py` (nonce-confirmed gate), `redaction.py`, `injection.py`, `denylist.py`, `audit.py` (SQLite WAL logging `input_mode` and `snapshot_id`) |
| `jarvis/voice/` | `wakeword.py` (openWakeWord listener), `stt.py` (Moonshine Small Streaming STT), `tts.py` (Pocket TTS), `buffer.py`, `vad.py`, `audio.py`, `ptt.py` |
| `jarvis/connectors/` | `windows_manager.py` (list/focus/resize/move/min/max/restore), `clipboard_safe.py` (redacted clipboard), `system_surfaces.py` (taskbar/tray/start), `files.py`, `powershell.py`, `graph.py`, `office_com.py`, `browser_cdp.py`, `spotify.py` |
| `jarvis/desktop/` | `adapter.py` (`DesktopAdapter` protocol, `UiaDesktopAdapter`, `MockDesktopAdapter`, `AgentDesktopSubprocessAdapter`), `orb.py` (3D transparent particles orb), `host.py`, `permissions.py` |
| `jarvis/capabilities.py` | Machine-readable capability discovery matrix (`jarvis capabilities --json`) |
| `jarvis/ui/` | `tray.py` (Windows system tray icon with Wake Word toggle checkbox), `overlay.py` |
| `jarvis/bench/` | `runner.py` (arms A-D, supports `--engine {state_machine, langgraph}`), `checkers.py`, `tasks/*.yaml` |

---

## Desktop Features & Transparent Particles Orb

The desktop agent includes a floating status and interaction widget:
- **Exact Web Particles Orb**: 360 golden-ratio Fibonacci spiral particles projected in real-time 3D, matching the web dashboard's visual style.
- **100% Transparent Background**: Configured with Windows transparent color-keying (`-transparentcolor "#010101"`). Only the animated particles and status text appear on screen.
- **Non-Activating Window**: Uses `WS_EX_TOOLWINDOW` and `WS_EX_NOACTIVATE` so the orb floats above active windows without stealing focus.
- **Draggable & Clickable**: Drag the orb anywhere on the screen, or click to toggle listening / push-to-talk.
- **Audio-Reactive States**:
  - `idle`: Gentle lavender/indigo drift and breathing.
  - `connecting`: Orbital ring formation.
  - `listening`: Emerald/blue ripple wave swelling with microphone volume.
  - `thinking`: Amber pulsing core.
  - `speaking`: Swirling fluid streams and energetic violet flow.
  - `error`: High-frequency jitter shake and rose/red alert glow.

---

## Quickstart (Windows)

```powershell
# 1. Install dependencies
cd jarvis
pip install -e .

# 2. Inspect platform and agent capabilities (JSON or formatted)
jarvis capabilities --json
jarvis capabilities

# 3. Verify setup & prerequisites
jarvis setup-check

# 4. Inspect active foreground accessibility tree
jarvis dump

# 5. Start the integrated desktop host (with Particles Orb + system tray)
jarvis desktop

# 6. Run an autonomous goal directly
# Classic state machine:
jarvis run jarvis/bench/tasks/bluetooth_toggle.yaml --planner scripted

# LangGraph checkpointing engine:
jarvis run jarvis/bench/tasks/bluetooth_toggle.yaml --engine langgraph

# 7. Run benchmark suite
jarvis bench --arms A,B,D --seeds 3

# 8. Run test suite
python -m pytest tests/ -q
```

---

## Voice Interaction Shortcuts

- **Push-to-Talk (PTT)**: Press `Left Ctrl + Space` or `Right Ctrl + Space` to start speaking. Press again to finish.
- **Tap-to-Speak**: Click the floating Particles Orb directly.
- **Wake Word**: When enabled via tray or `jarvis.toml` (`wakeword_enabled = true`), saying `"Hey Jarvis"` activates listening automatically.
- **System Tray**: Right-click the JARVIS icon in the notification area to toggle the wake word, pause, stop, or quit.
