# Graph Report - jarvis-personal-assistant  (2026-11-08)

## Corpus Check
- 171 files · ~88,366 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 2, .toml 2, .example 1)

## Summary
- 1614 nodes · 3715 edges · 121 communities (75 shown, 46 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 424 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c1fe9881`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SimulatedDesktop
- test_safety.py
- Safety Gate & Action Denylist
- ROADMAP.md
- time
- SessionMemory
- Orb
- test_agent.py
- WakeWord
- Bluetooth Benchmark Task
- MCP Client Connector
- os
- Test Core Module
- Agent Loop Detection
- run_spec
- Teams Draft Benchmark Task
- .run
- UserConsistentMemory
- Notepad Benchmark Task
- react
- Cli Module
- FastAPI Status & Server API
- 3. Phase-by-phase implementation plan
- EpisodicMemory
- Prompt Injection Benchmark
- orb/orb-state.ts
- FilesConnector
- desktop/package.json
- dependencies
- JarvisWebSocketService
- LoopDetector
- UIA Perception & Window Control
- Tray
- JARVIS API Contracts & IPC Protocol
- ProceduralMemory
- UIA Event Subscriptions
- speak
- host.py
- UIA Perception & Window Control
- Voice Activity Detection
- jarvisStore.ts
- office_com.py
- scripts
- JARVIS — Current State Audit & System Inventory
- nodes.py
- Phase 9 — Safety, privacy and security
- Usage
- graph.py
- Phase 6 — Upgrade the multi-agent intelligence architecture
- Phase 7 — Voice and conversational experience
- run_spec
- Phase 11 — Accessibility and user testing
- AgentBridge
- UiElement
- UIA MTA Worker Thread
- Phase 5 — Implement the action execution engine
- orb/use-audio-level.ts
- Fixture Mcp Server Module
- Phase 8 — Memory, personalisation and adaptive access
- Phase 6 — Upgrade the multi-agent intelligence architecture
- Phase 7 — Voice and conversational experience
- Phase 12 — Testing, packaging and public release
- Phase 2 — Build the native Windows application
- MoonshineSTTService
- Phase 10 — Integrations and advanced desktop capabilities
- startup.py
- test_voice_pipeline.py
- Overlay
- 2. Complete architecture and technology stack
- typing
- 2. Complete architecture and technology stack
- ocr.py
- MemoryManager
- Complete_Project_Implementation_Roadmap.md
- JARVIS Windows Automation Dependencies
- tauri.conf.json
- JARVIS for Windows: Autonomous UIA-First Desktop Agent & Voice Assistant
- compilerOptions
- state_machine.py
- Skill Recorder and Replay Engine
- UIA Set-of-Marks Perception
- Requirements Module
- Pyproject Module
- 3. Phase-by-phase implementation plan
- WakeWordService
- UiElement
- schemas.py
- lib.rs
- skills.py
- PocketTTSService
- Phase 3 — Establish Python ↔ Tauri communication
- Detailed Phase Breakdown
- orb/use-webgl-support.ts
- default.json
- Phase 9 — Safety, privacy and security
- Phase 11 — Accessibility and user testing
- UserFacts
- Phase 5 — Implement the action execution engine
- Phase 8 — Memory, personalisation and adaptive access
- Phase 12 — Testing, packaging and public release
- Phase 2 — Build the native Windows application
- Phase 10 — Integrations and advanced desktop capabilities
- jarvis-desktop

## God Nodes (most connected - your core abstractions)
1. `Screen` - 80 edges
2. `ActionResult` - 64 edges
3. `Step` - 56 edges
4. `MockExecutor` - 45 edges
5. `run_spec()` - 34 edges
6. `AgentBridge` - 33 edges
7. `SimulatedDesktop` - 32 edges
8. `run_task()` - 31 edges
9. `ConfirmationGate` - 28 edges
10. `Config` - 27 edges

## Surprising Connections (you probably didn't know these)
- `3. Critical Integration Gaps to Resolve in Milestone 1` --references--> `Config`  [INFERRED]
  docs/CURRENT_STATE_AUDIT.md → jarvis/jarvis/config.py
- `The Perception Cascade (Routes 1–4)` --references--> `UiElement`  [INFERRED]
  README.md → jarvis/jarvis/core/schema.py
- `1. Snapshot-scoped references instead of bare element marks` --references--> `Screen`  [INFERRED]
  docs/AGENT_DESKTOP_COMPARISON_AND_IMPROVEMENTS.md → jarvis/jarvis/core/schema.py
- `Unified 5-Tier Memory Architecture` --references--> `MemoryManager`  [INFERRED]
  README.md → jarvis/jarvis/memory/manager.py
- `Phase 3 — IPC and Lifecycle (`6/6 Complete` - 100%)` --references--> `JarvisWebSocketService`  [INFERRED]
  IMPLEMENTATION_PROGRESS.md → apps/desktop/src/services/websocket.ts

## Import Cycles
- None detected.

## Communities (121 total, 46 thin omitted)

### Community 0 - "SimulatedDesktop"
Cohesion: 0.10
Nodes (8): Architecture, Backlog, Implemented (2026-06-14), JARVIS for Windows — PRD, Not executed here (needs the user's Windows 11 machine), Original problem statement, Verified, SimulatedDesktop

### Community 1 - "test_safety.py"
Cohesion: 0.07
Nodes (45): blur_pii_boxes(), action_fingerprint(), is_denied(), always_deny_confirmer(), auto_approve_confirmer(), bind_hash(), ConfirmationGate, console_confirm() (+37 more)

### Community 2 - "Safety Gate & Action Denylist"
Cohesion: 0.05
Nodes (53): ActionResult, Executor, MockExecutor, act_click(), act_set_text(), clipboard_paste(), mouse_click_center(), _pat() (+45 more)

### Community 3 - "ROADMAP.md"
Cohesion: 0.12
Nodes (15): 10. One final recommendation: establish engineering discipline, 1. Define the final JARVIS product, 30.4%, 4. The actual development priority, 5. Features to postpone, 6. Suggested project management tracker, 7. Repository structure when the project is mature, 8. How to know when JARVIS is actually complete (+7 more)

### Community 4 - "time"
Cohesion: 0.37
Nodes (3): Fact, UserPreference, WorkingMemoryState

### Community 7 - "test_agent.py"
Cohesion: 0.23
Nodes (7): BudgetExceeded, Budgets, check_budget(), format_capabilities(), get_system_capabilities(), test_budget_exceeded(), test_capabilities_endpoint()

### Community 8 - "WakeWord"
Cohesion: 0.21
Nodes (4): WakeWord, audio_callback(), run_loop(), test_jarvis_wakeword_desktop()

### Community 9 - "Bluetooth Benchmark Task"
Cohesion: 0.08
Nodes (27): desired, reason, summary, type, url, ask_reply, check, equals (+19 more)

### Community 10 - "MCP Client Connector"
Cohesion: 0.17
Nodes (15): call_named_tool(), call_server_tool(), _gather(), list_all_tools(), list_server_tools(), load_servers(), McpToolRegistry, ServerConfig (+7 more)

### Community 11 - "os"
Cohesion: 0.24
Nodes (5): check_permissions(), open_accessibility_settings(), open_microphone_settings(), PermissionStatus, ensure_uia_type_library()

### Community 12 - "Test Core Module"
Cohesion: 0.22
Nodes (15): Diff, screen_diff(), _sig(), choose_route(), uia_confidence(), el(), screen(), test_choose_route_rules() (+7 more)

### Community 14 - "run_spec"
Cohesion: 0.19
Nodes (14): build_planner(), _observe(), run_benchmark(), run_spec(), _scripted_planner(), TaskSpec, _use_mock(), cfg() (+6 more)

### Community 15 - "Teams Draft Benchmark Task"
Cohesion: 0.08
Nodes (23): name, reason, summary, text, type, ask_reply, check, equals (+15 more)

### Community 16 - ".run"
Cohesion: 0.15
Nodes (6): speak_greeting(), on_frame(), start(), stop(), tap_to_speak(), PushToTalk

### Community 18 - "Notepad Benchmark Task"
Cohesion: 0.09
Nodes (21): keys, name, reason, summary, text, type, ask_reply, check (+13 more)

### Community 19 - "react"
Cohesion: 0.32
Nodes (8): lucide-react@^0.475.0, App(), fetchCapabilities(), useJarvisStore(), DashboardWindow(), OrbWindow(), lucide-react, react

### Community 20 - "Cli Module"
Cohesion: 0.21
Nodes (16): print_report(), cmd_bench(), cmd_capabilities(), cmd_desktop(), cmd_dump(), cmd_mcp(), cmd_run(), cmd_setup_check() (+8 more)

### Community 21 - "FastAPI Status & Server API"
Cohesion: 0.08
Nodes (17): assistant_respond(), AssistantRequest, AssistantResponse, create_status_check(), generate_speech(), get_capabilities(), get_status_checks(), health() (+9 more)

### Community 22 - "3. Phase-by-phase implementation plan"
Cohesion: 0.18
Nodes (11): 3. Phase-by-phase implementation plan, Implement a perception hierarchy, Implementation requirements, JARVIS perception engine, Phase 0 — Audit and stabilise your current application, Phase 1 — Refactor the Python engine into a modular backend, Phase 4 — Build the complete desktop perception engine, Proposed structure (+3 more)

### Community 24 - "Prompt Injection Benchmark"
Cohesion: 0.11
Nodes (17): reason, summary, type, url, ask_reply, check, cap, kind (+9 more)

### Community 25 - "orb/orb-state.ts"
Cohesion: 0.06
Nodes (62): hexChannel(), mixHex(), mixRgb(), Rgb, rgba(), rgbToHex(), shadeHex(), tintHex() (+54 more)

### Community 26 - "FilesConnector"
Cohesion: 0.47
Nodes (3): FilesConnector, _res(), test_files_connector_crud()

### Community 27 - "desktop/package.json"
Cohesion: 0.11
Nodes (25): devDependencies, autoprefixer@^10.4.20, postcss@^8.4.49, tailwindcss@^3.4.17, @tauri-apps/cli@^2.2.0, @types/node@^22.0.0, @types/react@^18.3.1, @types/react-dom@^18.3.1 (+17 more)

### Community 28 - "dependencies"
Cohesion: 0.20
Nodes (10): dependencies, react@^18.3.1, react-dom@^18.3.1, @tauri-apps/api@^2.2.0, @tauri-apps/plugin-global-shortcut@^2.2.0, @tauri-apps/plugin-shell@^2.2.0, react-dom, @tauri-apps/api (+2 more)

### Community 31 - "UIA Perception & Window Control"
Cohesion: 0.21
Nodes (5): _app_window(), collect(), build_screen(), _is_usable_app_window(), snapshot_foreground()

### Community 33 - "JARVIS API Contracts & IPC Protocol"
Cohesion: 0.25
Nodes (7): 1. WebSocket Protocol Structure, 2. Command Catalog, 3. Event Catalog, 4. REST Endpoints, Command Envelope (Client -> Server), Event Envelope (Server -> Client), JARVIS API Contracts & IPC Protocol

### Community 35 - "UIA Event Subscriptions"
Cohesion: 0.18
Nodes (4): Events, install_events(), last_event_time(), wait_idle_polling()

### Community 36 - "speak"
Cohesion: 0.36
Nodes (4): speak(), speak_pocket_tts(), speak_pyttsx3(), speak_winrt()

### Community 38 - "UIA Perception & Window Control"
Cohesion: 0.12
Nodes (3): PerceptionBackend, UiaBackend, UiaThread

### Community 41 - "jarvisStore.ts"
Cohesion: 0.28
Nodes (12): EventCallback, wsService, globalState, JarvisState, listeners, notify(), setJarvisState(), ApprovalRequest (+4 more)

### Community 43 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, preview, tauri

### Community 44 - "JARVIS — Current State Audit & System Inventory"
Cohesion: 0.40
Nodes (4): 1. Executive Summary, 2. Feature & Component Matrix, 3. Critical Integration Gaps to Resolve in Milestone 1, JARVIS — Current State Audit & System Inventory

### Community 45 - "nodes.py"
Cohesion: 0.11
Nodes (16): verify_step(), VerifyResult, _serialize_val(), SqliteCheckpointer, GraphEngine, act_node(), consolidate_node(), gate_node() (+8 more)

### Community 46 - "Phase 9 — Safety, privacy and security"
Cohesion: 0.40
Nodes (5): Important design principle, Phase 9 — Safety, privacy and security, Privacy gateway, Safety tiers, Security checklist

### Community 47 - "Usage"
Cohesion: 0.06
Nodes (36): classify_script(), run_powershell(), auth_url(), exchange_code(), pkce_pair(), play(), search(), build_step_message() (+28 more)

### Community 48 - "graph.py"
Cohesion: 0.70
Nodes (4): create_draft(), _msal_app(), send_draft(), token()

### Community 49 - "Phase 6 — Upgrade the multi-agent intelligence architecture"
Cohesion: 0.50
Nodes (4): Additional requirements, Phase 6 — Upgrade the multi-agent intelligence architecture, Proposed agent architecture, Responsibilities

### Community 50 - "Phase 7 — Voice and conversational experience"
Cohesion: 0.50
Nodes (4): Conversational recovery, Implement, Phase 7 — Voice and conversational experience, Voice pipeline

### Community 52 - "Phase 11 — Accessibility and user testing"
Cohesion: 0.50
Nodes (4): Accessibility UI requirements, Input methods, Phase 11 — Accessibility and user testing, Real-user validation

### Community 53 - "AgentBridge"
Cohesion: 0.19
Nodes (10): api_websocket(), cancel_task(), get_task_status(), respond_approval(), submit_task(), ActiveTask, AgentBridge, bridge_confirmer() (+2 more)

### Community 54 - "UiElement"
Cohesion: 0.20
Nodes (9): element_key(), Rect, UiElement, MockWindow, assign_marks(), rank(), test_element_key_stable_and_distinct(), test_rank_and_marks_focused_first() (+1 more)

### Community 56 - "Phase 5 — Implement the action execution engine"
Cohesion: 0.50
Nodes (4): Action types, Execution requirements, Phase 5 — Implement the action execution engine, Standard action envelope

### Community 57 - "orb/use-audio-level.ts"
Cohesion: 0.24
Nodes (16): AudioBands, normalize(), useAudioBands(), acquireSharedAnalyser(), AudioLevel, AudioLevelError, classifyAudioError(), createShared() (+8 more)

### Community 59 - "Phase 8 — Memory, personalisation and adaptive access"
Cohesion: 0.50
Nodes (4): Adaptive interaction profiles, Implementation requirements, Phase 8 — Memory, personalisation and adaptive access, Proposed memory system

### Community 60 - "Phase 6 — Upgrade the multi-agent intelligence architecture"
Cohesion: 0.50
Nodes (4): Additional requirements, Phase 6 — Upgrade the multi-agent intelligence architecture, Proposed agent architecture, Responsibilities

### Community 61 - "Phase 7 — Voice and conversational experience"
Cohesion: 0.50
Nodes (4): Conversational recovery, Implement, Phase 7 — Voice and conversational experience, Voice pipeline

### Community 62 - "Phase 12 — Testing, packaging and public release"
Cohesion: 0.50
Nodes (4): Final release features, Phase 12 — Testing, packaging and public release, Production packaging, Testing strategy

### Community 63 - "Phase 2 — Build the native Windows application"
Cohesion: 0.50
Nodes (4): Frontend structure, Native Windows features, Phase 2 — Build the native Windows application, Windows you should build

### Community 64 - "MoonshineSTTService"
Cohesion: 0.17
Nodes (3): MoonshineStreamSession, MoonshineSTTService, test_stt_service_initialization()

### Community 66 - "Phase 10 — Integrations and advanced desktop capabilities"
Cohesion: 0.50
Nodes (4): Integration architecture, MCP support, Phase 10 — Integrations and advanced desktop capabilities, Suggested integrations

### Community 68 - "test_voice_pipeline.py"
Cohesion: 0.16
Nodes (7): get_voice_config(), update_voice_config(), VoiceConfig, VoiceConfigUpdate, Transcriber, test_jarvis_stt_desktop(), test_voice_config_api_functions()

### Community 70 - "2. Complete architecture and technology stack"
Cohesion: 0.67
Nodes (3): 2. Complete architecture and technology stack, JARVIS technology stack, One important architectural rule

### Community 71 - "typing"
Cohesion: 0.05
Nodes (29): 1. Snapshot-scoped references instead of bare element marks, 2. A stable JSON envelope for every tool operation, 3. Headless should be the default, 4. Dense screens need two-stage observation, 5. Broader desktop surface coverage, 6. Capability discovery should be built in, 7. Make the observe-act-verify contract explicit, 8. Separate the desktop adapter from the planner (+21 more)

### Community 72 - "2. Complete architecture and technology stack"
Cohesion: 0.67
Nodes (3): 2. Complete architecture and technology stack, JARVIS technology stack, One important architectural rule

### Community 75 - "Complete_Project_Implementation_Roadmap.md"
Cohesion: 0.12
Nodes (15): 10. One final recommendation: establish engineering discipline, 1. Define the final JARVIS product, 30.4%, 4. The actual development priority, 5. Features to postpone, 6. Suggested project management tracker, 7. Repository structure when the project is mature, 8. How to know when JARVIS is actually complete (+7 more)

### Community 77 - "tauri.conf.json"
Cohesion: 0.11
Nodes (17): app, security, windows, build, beforeBuildCommand, beforeDevCommand, devUrl, frontendDist (+9 more)

### Community 78 - "JARVIS for Windows: Autonomous UIA-First Desktop Agent & Voice Assistant"
Cohesion: 0.05
Nodes (38): 1. High-Level Architectural Topology, 2. Component Directory Boundaries, 3.1. Desktop Windowing & Orb, 3.2. Perception Cascade (Routes 1–4), 3.3. Five-Tier Safety Gate, 3. Core Subsystems, JARVIS System Architecture, 1. Python Environment Setup (+30 more)

### Community 79 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+9 more)

### Community 80 - "state_machine.py"
Cohesion: 0.17
Nodes (13): ProgressMemory, AgentContext, _ask(), _diff_line(), _route_str(), run_task(), finish(), TaskOutcome (+5 more)

### Community 99 - "3. Phase-by-phase implementation plan"
Cohesion: 0.18
Nodes (11): 3. Phase-by-phase implementation plan, Implement a perception hierarchy, Implementation requirements, JARVIS perception engine, Phase 0 — Audit and stabilise your current application, Phase 1 — Refactor the Python engine into a modular backend, Phase 4 — Build the complete desktop perception engine, Proposed structure (+3 more)

### Community 101 - "UiElement"
Cohesion: 0.23
Nodes (9): ScriptError, Screen, _flags(), serialize(), serialize_screen(), serialize_skeleton(), serialize_subtree(), test_screen_snapshot_id_and_refs() (+1 more)

### Community 105 - "schemas.py"
Cohesion: 0.30
Nodes (8): Phase 1 — Python Engine Modularization (`6/6 Complete` - 100%), ApprovalResponseData, CommandEnvelope, CommandType, Envelope, EventEnvelope, EventType, TaskSubmitData

### Community 107 - "lib.rs"
Cohesion: 0.33
Nodes (3): run(), toggle_dashboard(), toggle_orb()

### Community 110 - "skills.py"
Cohesion: 0.12
Nodes (12): planner_from_skill(), record_skill(), replay_skill(), ScriptedPlanner, ScriptEntry, checker_element_state(), run_checkers(), match_selector() (+4 more)

### Community 118 - "Phase 3 — Establish Python ↔ Tauri communication"
Cohesion: 0.15
Nodes (10): Communication design, Define command contracts, Define event contracts, Phase 3 — Establish Python ↔ Tauri communication, Process lifecycle, Communication design, Define command contracts, Define event contracts (+2 more)

### Community 119 - "Detailed Phase Breakdown"
Cohesion: 0.25
Nodes (7): Detailed Phase Breakdown, JARVIS Project Implementation Progress Tracker, Next Milestone: Milestone 2 — Autonomous AI Desktop Agent (Phases 4–6), Phase 0 — Audit & Stabilize (`5/5 Complete` - 100%), Phase 2 — Native Desktop Application (`7/7 Complete` - 100%), Phase 3 — IPC and Lifecycle (`6/6 Complete` - 100%), Progress Dashboard

### Community 124 - "orb/use-webgl-support.ts"
Cohesion: 0.60
Nodes (5): detect(), getServerSnapshot(), getSnapshot(), subscribe(), useWebGLSupport()

### Community 125 - "default.json"
Cohesion: 0.33
Nodes (5): description, identifier, permissions, $schema, windows

### Community 129 - "Phase 9 — Safety, privacy and security"
Cohesion: 0.40
Nodes (5): Important design principle, Phase 9 — Safety, privacy and security, Privacy gateway, Safety tiers, Security checklist

### Community 131 - "Phase 11 — Accessibility and user testing"
Cohesion: 0.50
Nodes (4): Accessibility UI requirements, Input methods, Phase 11 — Accessibility and user testing, Real-user validation

### Community 135 - "Phase 5 — Implement the action execution engine"
Cohesion: 0.50
Nodes (4): Action types, Execution requirements, Phase 5 — Implement the action execution engine, Standard action envelope

### Community 136 - "Phase 8 — Memory, personalisation and adaptive access"
Cohesion: 0.50
Nodes (4): Adaptive interaction profiles, Implementation requirements, Phase 8 — Memory, personalisation and adaptive access, Proposed memory system

### Community 138 - "Phase 12 — Testing, packaging and public release"
Cohesion: 0.50
Nodes (4): Final release features, Phase 12 — Testing, packaging and public release, Production packaging, Testing strategy

### Community 139 - "Phase 2 — Build the native Windows application"
Cohesion: 0.50
Nodes (4): Frontend structure, Native Windows features, Phase 2 — Build the native Windows application, Windows you should build

### Community 141 - "Phase 10 — Integrations and advanced desktop capabilities"
Cohesion: 0.50
Nodes (4): Integration architecture, MCP support, Phase 10 — Integrations and advanced desktop capabilities, Suggested integrations

## Knowledge Gaps
- **7 isolated node(s):** `jarvis-desktop`, `jarvis-win`, `UIA MTA Worker Thread`, `JARVIS Windows Automation Dependencies`, `Skill Recorder and Replay Engine` (+2 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 579 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **46 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AgentBridge` connect `AgentBridge` to `SimulatedDesktop`, `test_safety.py`, `Safety Gate & Action Denylist`, `test_agent.py`, `schemas.py`, `skills.py`, `state_machine.py`, `run_spec`, `Cli Module`, `Detailed Phase Breakdown`, `FilesConnector`?**
  _High betweenness centrality (0.203) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Screen` (e.g. with `1. Snapshot-scoped references instead of bare element marks` and `Phase 1 — reliability contract`) actually correct?**
  _`Screen` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `jarvis-desktop`, `jarvis-win`, `UIA MTA Worker Thread` to the rest of the system?**
  _7 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SimulatedDesktop` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Why does `Phase 3 — IPC and Lifecycle (`6/6 Complete` - 100%)` connect `Detailed Phase Breakdown` to `AgentBridge`, `JarvisWebSocketService`?**
  _High betweenness centrality (0.188) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `ActionResult` (e.g. with `ActionEnvelope` and `ActionError`) actually correct?**
  _`ActionResult` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_safety.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07135135135135136 - nodes in this community are weakly interconnected._