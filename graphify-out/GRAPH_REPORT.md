# Graph Report - jarvis-personal-assistant  (2026-11-08)

## Corpus Check
- 258 files · ~100,005 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 19 file(s) not represented in the graph (top: (none) 7, .css 4, .toml 2)

## Summary
- 2228 nodes · 4913 edges · 162 communities (91 shown, 71 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 429 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `416a139d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- compilerOptions
- test_safety.py
- Safety Gate & Action Denylist
- Context-Menu Module
- Frontend Build Tooling
- dependencies
- Frontend Build Tooling
- test_agent.py
- WakeWord
- Bluetooth Benchmark Task
- MCP Client Connector
- alert-dialog.jsx
- Test Core Module
- Agent Loop Detection
- run_spec
- Teams Draft Benchmark Task
- .run
- Use-Toast Module
- Notepad Benchmark Task
- react
- Cli Module
- FastAPI Status & Server API
- Shadcn UI Configuration
- UI Command Palette
- Prompt Injection Benchmark
- orb/orb-state.ts
- runner.py
- desktop/package.json
- navigation-menu.jsx
- Recorded Bluetooth Skills
- Recorded Bluetooth Skills
- UIA Perception & Window Control
- frontend/src/registry/lib/use-orb-animator.ts
- Transcriber
- form.jsx
- UIA Event Subscriptions
- Screen
- host.py
- UIA Perception & Window Control
- Voice Activity Detection
- frontend/src/registry/orbe/particles-orb/particles-orb.tsx
- jarvisStore.ts
- breadcrumb.jsx
- Craco.Config Module
- Drawer Module
- nodes.py
- lucide-react
- Usage
- Sheet Module
- ProgressMemory
- Webpack-Health-Plugin Module
- run_spec
- Frontend Dependencies
- AgentBridge
- Rect
- JARVIS Product Requirements
- Jsconfig Module
- orb/use-audio-level.ts
- Fixture Mcp Server Module
- Frontend Dependencies
- Health-Endpoints Module
- compilerOptions
- browserslist
- UI Component Dependencies
- MoonshineSTTService
- frontend/src/registry/lib/orb-state.ts
- utils.js
- test_voice_pipeline.py
- frontend/src/registry/lib/use-audio-level.ts
- @radix-ui/react-collapsible
- typing
- frontend/src/registry/lib/orb-pill.tsx
- Important ideas to take from `agent-desktop`
- MemoryManager
- Complete_Project_Implementation_Roadmap.md
- @radix-ui/react-select
- tauri.conf.json
- JARVIS for Windows: Autonomous UIA-First Desktop Agent & Voice Assistant
- compilerOptions
- state_machine.py
- Readme Module
- Readme Module
- Requirements Module
- Readme Module
- JARVIS Product Requirements
- Pyproject Module
- 3. Phase-by-phase implementation plan
- WakeWordService
- UiElement
- AgentDesktopSubprocessAdapter
- react-dom@19.0.0
- lib/use-orb-cues.ts
- schemas.py
- frontend/src/registry/lib/use-webgl-support.ts
- lib.rs
- react-scripts@5.0.1
- test_vertical_slice_e2e.py
- checkers.py
- JARVIS API Contracts & IPC Protocol
- PocketTTSService
- select.jsx
- 3. Core Subsystems
- Phase 3 — Establish Python ↔ Tauri communication
- Detailed Phase Breakdown
- embla-carousel-react
- @radix-ui/react-avatar
- DesktopAdapter
- orb/use-webgl-support.ts
- default.json
- SafetyReviewerAgent
- @radix-ui/react-menubar
- PerceptionBackend
- Phase 9 — Safety, privacy and security
- JARVIS — Current State Audit & System Inventory
- Phase 11 — Accessibility and user testing
- UserFacts
- lodash@4.18.1
- clsx
- Phase 5 — Implement the action execution engine
- Phase 8 — Memory, personalisation and adaptive access
- @radix-ui/react-progress
- Phase 12 — Testing, packaging and public release
- Phase 2 — Build the native Windows application
- @radix-ui/react-tabs
- Phase 10 — Integrations and advanced desktop capabilities
- react-day-picker
- Phase 1 — Refactor the Python engine into a modular backend
- zod@3.24.4
- cra-template@1.2.0
- framer-motion@11.18.0
- lucide-react@0.516.0
- @radix-ui/react-context-menu
- @radix-ui/react-dialog
- @radix-ui/react-dropdown-menu
- @radix-ui/react-hover-card
- @radix-ui/react-radio-group
- @radix-ui/react-toggle
- react-resizable-panels
- tailwindcss-animate@1.0.7
- @tanstack/react-query
- jarvis-desktop

## God Nodes (most connected - your core abstractions)
1. `cn()` - 195 edges
2. `Screen` - 80 edges
3. `ActionResult` - 64 edges
4. `Step` - 56 edges
5. `MockExecutor` - 45 edges
6. `resolutions` - 43 edges
7. `run_spec()` - 34 edges
8. `AgentBridge` - 33 edges
9. `run_task()` - 31 edges
10. `SimulatedDesktop` - 31 edges

## Surprising Connections (you probably didn't know these)
- `3. Critical Integration Gaps to Resolve in Milestone 1` --references--> `Config`  [INFERRED]
  CURRENT_STATE_AUDIT.md → jarvis/jarvis/config.py
- `The Perception Cascade (Routes 1–4)` --references--> `UiElement`  [INFERRED]
  README.md → jarvis/jarvis/core/schema.py
- `1. Snapshot-scoped references instead of bare element marks` --references--> `Screen`  [INFERRED]
  AGENT_DESKTOP_COMPARISON_AND_IMPROVEMENTS.md → jarvis/jarvis/core/schema.py
- `Headless-by-Default Policy & Input Mode Auditing` --references--> `Toggle`  [INFERRED]
  README.md → jarvis/jarvis/core/schema.py
- `8. Separate the desktop adapter from the planner` --references--> `DesktopAdapter`  [INFERRED]
  AGENT_DESKTOP_COMPARISON_AND_IMPROVEMENTS.md → jarvis/jarvis/desktop/adapter.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **JARVIS Windows Core Architecture** — memory_prd_jarvis_windows_agent, jarvis_readme_uia_worker, memory_prd_perception_cascade, memory_prd_safety_gate [EXTRACTED 1.00]

## Communities (162 total, 71 thin omitted)

### Community 0 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, allowSyntheticDefaultImports, baseUrl, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx (+11 more)

### Community 1 - "test_safety.py"
Cohesion: 0.06
Nodes (58): Executor, classify_script(), run_powershell(), auth_url(), exchange_code(), pkce_pair(), play(), search() (+50 more)

### Community 2 - "Safety Gate & Action Denylist"
Cohesion: 0.06
Nodes (46): ActionResult, MockExecutor, act_click(), act_set_text(), clipboard_paste(), mouse_click_center(), _pat(), _rect_to_center() (+38 more)

### Community 3 - "Context-Menu Module"
Cohesion: 0.06
Nodes (50): Avatar, AvatarFallback, AvatarImage, Card, CardContent, CardDescription, CardFooter, CardHeader (+42 more)

### Community 4 - "Frontend Build Tooling"
Cohesion: 0.05
Nodes (43): resolutions, **/anymatch/picomatch, **/axios/form-data, @babel/plugin-transform-modules-systemjs, **/cosmiconfig/yaml, **/css-loader/postcss, **/css-minimizer-webpack-plugin/postcss, **/cssnano/yaml (+35 more)

### Community 5 - "dependencies"
Cohesion: 0.04
Nodes (45): dependencies, axios@1.20.0, class-variance-authority@0.7.1, cmdk@1.1.1, date-fns@4.1.0, dayjs@1.11.13, @hookform/resolvers@5.0.1, input-otp@1.4.2 (+37 more)

### Community 6 - "Frontend Build Tooling"
Cohesion: 0.07
Nodes (41): devDependencies, ajv@^8.20.0, ajv-keywords@^5.1.0, autoprefixer@10.4.20, @babel/plugin-proposal-private-property-in-object@7.21.11, @craco/craco@7.1.0, dotenv@16.4.5, @emergentbase/overlay@https://assets.emergent.sh/npm/emerge... (+33 more)

### Community 7 - "test_agent.py"
Cohesion: 0.20
Nodes (6): BudgetExceeded, Budgets, check_budget(), LoopDetector, test_budget_exceeded(), test_loop_detector_triggers()

### Community 8 - "WakeWord"
Cohesion: 0.10
Nodes (13): create_draft(), _msal_app(), send_draft(), token(), check_permissions(), open_accessibility_settings(), open_microphone_settings(), PermissionStatus (+5 more)

### Community 9 - "Bluetooth Benchmark Task"
Cohesion: 0.08
Nodes (27): desired, reason, summary, type, url, ask_reply, check, equals (+19 more)

### Community 10 - "MCP Client Connector"
Cohesion: 0.17
Nodes (15): call_named_tool(), call_server_tool(), _gather(), list_all_tools(), list_server_tools(), load_servers(), McpToolRegistry, ServerConfig (+7 more)

### Community 11 - "alert-dialog.jsx"
Cohesion: 0.11
Nodes (25): AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter(), AlertDialogHeader(), AlertDialogOverlay, AlertDialogTitle (+17 more)

### Community 12 - "Test Core Module"
Cohesion: 0.19
Nodes (17): Diff, screen_diff(), _sig(), choose_route(), uia_confidence(), el(), screen(), test_action_union_discriminated() (+9 more)

### Community 14 - "run_spec"
Cohesion: 0.15
Nodes (18): record_skill(), replay_skill(), build_planner(), run_benchmark(), run_spec(), TaskSpec, match_selector(), resolve_element() (+10 more)

### Community 15 - "Teams Draft Benchmark Task"
Cohesion: 0.08
Nodes (23): name, reason, summary, text, type, ask_reply, check, equals (+15 more)

### Community 16 - ".run"
Cohesion: 0.06
Nodes (11): speak_greeting(), on_frame(), start(), stop(), tap_to_speak(), Orb, Tray, speak() (+3 more)

### Community 17 - "Use-Toast Module"
Cohesion: 0.18
Nodes (18): Toast, ToastAction, ToastClose, ToastDescription, ToastTitle, toastVariants, ToastViewport, Toaster() (+10 more)

### Community 18 - "Notepad Benchmark Task"
Cohesion: 0.09
Nodes (21): keys, name, reason, summary, text, type, ask_reply, check (+13 more)

### Community 19 - "react"
Cohesion: 0.13
Nodes (14): App(), Home(), Badge(), badgeVariants, PopoverContent, Switch, VoiceSettings(), LOGIN (+6 more)

### Community 20 - "Cli Module"
Cohesion: 0.23
Nodes (15): print_report(), cmd_bench(), cmd_capabilities(), cmd_desktop(), cmd_dump(), cmd_mcp(), cmd_run(), cmd_setup_check() (+7 more)

### Community 21 - "FastAPI Status & Server API"
Cohesion: 0.08
Nodes (17): assistant_respond(), AssistantRequest, AssistantResponse, create_status_check(), generate_speech(), get_capabilities(), get_status_checks(), health() (+9 more)

### Community 22 - "Shadcn UI Configuration"
Cohesion: 0.11
Nodes (17): aliases, components, hooks, lib, ui, utils, iconLibrary, rsc (+9 more)

### Community 23 - "UI Command Palette"
Cohesion: 0.14
Nodes (15): Command, CommandDialog(), CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator (+7 more)

### Community 24 - "Prompt Injection Benchmark"
Cohesion: 0.11
Nodes (17): reason, summary, type, url, ask_reply, check, cap, kind (+9 more)

### Community 25 - "orb/orb-state.ts"
Cohesion: 0.06
Nodes (62): hexChannel(), mixHex(), mixRgb(), Rgb, rgba(), rgbToHex(), shadeHex(), tintHex() (+54 more)

### Community 26 - "runner.py"
Cohesion: 0.15
Nodes (10): planner_from_skill(), ScriptedPlanner, ScriptEntry, ActiveTask, _observe(), _scripted_planner(), _use_mock(), FilesConnector (+2 more)

### Community 27 - "desktop/package.json"
Cohesion: 0.06
Nodes (43): dependencies, lucide-react@^0.475.0, react@^18.3.1, react-dom@^18.3.1, @tauri-apps/api@^2.2.0, @tauri-apps/plugin-global-shortcut@^2.2.0, @tauri-apps/plugin-shell@^2.2.0, devDependencies (+35 more)

### Community 28 - "navigation-menu.jsx"
Cohesion: 0.32
Nodes (7): NavigationMenu, NavigationMenuContent, NavigationMenuIndicator, NavigationMenuList, NavigationMenuTrigger, navigationMenuTriggerStyle, NavigationMenuViewport

### Community 29 - "Recorded Bluetooth Skills"
Cohesion: 0.12
Nodes (15): desired, reason, summary, type, url, name, params, automation_id (+7 more)

### Community 30 - "Recorded Bluetooth Skills"
Cohesion: 0.12
Nodes (15): desired, name, reason, summary, type, name, params, automation_id (+7 more)

### Community 31 - "UIA Perception & Window Control"
Cohesion: 0.17
Nodes (5): _app_window(), collect(), _is_usable_app_window(), snapshot_foreground(), Overlay

### Community 32 - "frontend/src/registry/lib/use-orb-animator.ts"
Cohesion: 0.21
Nodes (18): approach(), blendEnergy(), createStateMix(), observeActivity(), useInView(), isSettled(), LEVEL_ATTACK_RATE, LEVEL_RELEASE_RATE (+10 more)

### Community 34 - "form.jsx"
Cohesion: 0.24
Nodes (10): FormControl, FormDescription, FormFieldContext, FormItem, FormItemContext, FormLabel, FormMessage, useFormField() (+2 more)

### Community 35 - "UIA Event Subscriptions"
Cohesion: 0.18
Nodes (4): Events, install_events(), last_event_time(), wait_idle_polling()

### Community 36 - "Screen"
Cohesion: 0.11
Nodes (9): MockDesktopAdapter, UiaDesktopAdapter, WindowInfo, Desktop Control & Reliability Enhancements, Desktop Surface Connectors, Headless-by-Default Policy & Input Mode Auditing, Pluggable `DesktopAdapter` Protocol, Snapshot-Scoped References & Stale Target Defense (+1 more)

### Community 40 - "frontend/src/registry/orbe/particles-orb/particles-orb.tsx"
Cohesion: 0.14
Nodes (21): hexChannel(), mixHex(), mixRgb(), Rgb, rgba(), rgbToHex(), shadeHex(), tintHex() (+13 more)

### Community 41 - "jarvisStore.ts"
Cohesion: 0.10
Nodes (18): App(), fetchCapabilities(), EventCallback, JarvisWebSocketService, wsService, globalState, JarvisState, listeners (+10 more)

### Community 42 - "breadcrumb.jsx"
Cohesion: 0.20
Nodes (9): @radix-ui/react-slot@1.2.0, Breadcrumb, BreadcrumbEllipsis(), BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator() (+1 more)

### Community 43 - "Craco.Config Module"
Cohesion: 0.25
Nodes (6): config, makeDevServerV5Compatible(), path, webpackConfig, @emergentbase/visual-edits@https://assets.emergent.sh/npm/emerge..., @emergentbase/visual-edits

### Community 44 - "Drawer Module"
Cohesion: 0.29
Nodes (6): DrawerContent, DrawerDescription, DrawerFooter(), DrawerHeader(), DrawerOverlay, DrawerTitle

### Community 45 - "nodes.py"
Cohesion: 0.11
Nodes (16): verify_step(), VerifyResult, _serialize_val(), SqliteCheckpointer, GraphEngine, act_node(), consolidate_node(), gate_node() (+8 more)

### Community 46 - "lucide-react"
Cohesion: 0.15
Nodes (8): AccordionContent, AccordionItem, AccordionTrigger, Checkbox, RadioGroup, RadioGroupItem, ResizableHandle(), ResizablePanelGroup()

### Community 47 - "Usage"
Cohesion: 0.06
Nodes (27): build_step_message(), system_prompt(), step_schema(), est_tokens(), extract_json(), LLMError, PlannerLLM, Usage (+19 more)

### Community 48 - "Sheet Module"
Cohesion: 0.18
Nodes (12): Alert, AlertDescription, AlertTitle, alertVariants, SheetContent, SheetDescription, SheetFooter(), SheetHeader() (+4 more)

### Community 52 - "Frontend Dependencies"
Cohesion: 0.33
Nodes (4): next-themes@0.4.6, sonner@2.0.3, next-themes, sonner

### Community 53 - "AgentBridge"
Cohesion: 0.17
Nodes (10): api_websocket(), cancel_task(), get_task_status(), respond_approval(), submit_task(), AgentBridge, bridge_confirmer(), event_callback() (+2 more)

### Community 55 - "JARVIS Product Requirements"
Cohesion: 0.29
Nodes (6): UIA MTA Worker Thread, JARVIS Windows Automation Dependencies, JARVIS for Windows Agent, Nonce-Confirmed Safety Gate, Simulated Desktop Environment, Testing and Verification Protocol

### Community 56 - "Jsconfig Module"
Cohesion: 0.40
Nodes (4): compilerOptions, baseUrl, paths, include

### Community 57 - "orb/use-audio-level.ts"
Cohesion: 0.24
Nodes (16): AudioBands, normalize(), useAudioBands(), acquireSharedAnalyser(), AudioLevel, AudioLevelError, classifyAudioError(), createShared() (+8 more)

### Community 59 - "Frontend Dependencies"
Cohesion: 0.50
Nodes (4): scripts, build, start, test

### Community 61 - "compilerOptions"
Cohesion: 0.10
Nodes (19): compilerOptions, allowJs, baseUrl, esModuleInterop, forceConsistentCasingInFileNames, incremental, isolatedModules, jsx (+11 more)

### Community 62 - "browserslist"
Cohesion: 0.67
Nodes (3): browserslist, development, production

### Community 64 - "MoonshineSTTService"
Cohesion: 0.19
Nodes (3): MoonshineStreamSession, MoonshineSTTService, test_stt_service_initialization()

### Community 66 - "frontend/src/registry/lib/orb-state.ts"
Cohesion: 0.11
Nodes (17): ENTER_RATE, ERROR_COLOR_FROM, ERROR_COLOR_TO, ERROR_RATE, ORB_STATES, OrbMotion, OrbState, SETTLE_RATE (+9 more)

### Community 67 - "utils.js"
Cohesion: 0.09
Nodes (15): HoverCardContent, Input, Progress, ScrollArea, ScrollBar, Separator, Skeleton(), Slider (+7 more)

### Community 68 - "test_voice_pipeline.py"
Cohesion: 0.16
Nodes (6): get_voice_config(), update_voice_config(), VoiceConfig, VoiceConfigUpdate, blur_pii_boxes(), test_voice_config_api_functions()

### Community 69 - "frontend/src/registry/lib/use-audio-level.ts"
Cohesion: 0.24
Nodes (16): AudioBands, normalize(), useAudioBands(), acquireSharedAnalyser(), AudioLevel, AudioLevelError, classifyAudioError(), createShared() (+8 more)

### Community 71 - "typing"
Cohesion: 0.23
Nodes (5): MultiAgentCoordinator, MemorySpecialistAgent, SubTask, SupervisorAgent, VoiceInteractionAgent

### Community 72 - "frontend/src/registry/lib/orb-pill.tsx"
Cohesion: 0.16
Nodes (16): DEFAULT_ORB_MESSAGES, isShimmerState(), Letters(), Line, messageList(), ORB_PX, OrbMessages, OrbPill() (+8 more)

### Community 73 - "Important ideas to take from `agent-desktop`"
Cohesion: 0.11
Nodes (18): 1. Snapshot-scoped references instead of bare element marks, 2. A stable JSON envelope for every tool operation, 3. Headless should be the default, 4. Dense screens need two-stage observation, 5. Broader desktop surface coverage, 6. Capability discovery should be built in, 7. Make the observe-act-verify contract explicit, 8. Separate the desktop adapter from the planner (+10 more)

### Community 74 - "MemoryManager"
Cohesion: 0.05
Nodes (11): EpisodicMemory, MemoryManager, ProceduralMemory, SessionMemory, EpisodicRecord, Fact, SessionCheckpoint, UserPreference (+3 more)

### Community 75 - "Complete_Project_Implementation_Roadmap.md"
Cohesion: 0.11
Nodes (18): 10. One final recommendation: establish engineering discipline, 1. Define the final JARVIS product, 2. Complete architecture and technology stack, 30.4%, 4. The actual development priority, 5. Features to postpone, 6. Suggested project management tracker, 7. Repository structure when the project is mature (+10 more)

### Community 77 - "tauri.conf.json"
Cohesion: 0.11
Nodes (17): app, security, windows, build, beforeBuildCommand, beforeDevCommand, devUrl, frontendDist (+9 more)

### Community 78 - "JARVIS for Windows: Autonomous UIA-First Desktop Agent & Voice Assistant"
Cohesion: 0.12
Nodes (15): CLI Reference, Core Capabilities:, JARVIS for Windows: Autonomous UIA-First Desktop Agent & Voice Assistant, License, Machine-Readable Capabilities Discovery, Overview & What JARVIS Can Do, Particles Orb UI (Web & Desktop), Running Tests (+7 more)

### Community 79 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+9 more)

### Community 80 - "state_machine.py"
Cohesion: 0.25
Nodes (11): AgentContext, _ask(), _diff_line(), _route_str(), run_task(), finish(), TaskOutcome, TaskState (+3 more)

### Community 99 - "3. Phase-by-phase implementation plan"
Cohesion: 0.12
Nodes (16): 3. Phase-by-phase implementation plan, Additional requirements, Conversational recovery, Implement, Implement a perception hierarchy, JARVIS perception engine, Phase 0 — Audit and stabilise your current application, Phase 4 — Build the complete desktop perception engine (+8 more)

### Community 101 - "UiElement"
Cohesion: 0.17
Nodes (15): ScriptError, Screen, UiElement, MockWindow, assign_marks(), _flags(), rank(), serialize() (+7 more)

### Community 104 - "lib/use-orb-cues.ts"
Cohesion: 0.33
Nodes (6): Cue, CUES, CueTone, OrbCuesOptions, playCue(), useOrbCues()

### Community 105 - "schemas.py"
Cohesion: 0.30
Nodes (8): Phase 1 — Python Engine Modularization (`6/6 Complete` - 100%), ApprovalResponseData, CommandEnvelope, CommandType, Envelope, EventEnvelope, EventType, TaskSubmitData

### Community 106 - "frontend/src/registry/lib/use-webgl-support.ts"
Cohesion: 0.60
Nodes (5): detect(), getServerSnapshot(), getSnapshot(), subscribe(), useWebGLSupport()

### Community 107 - "lib.rs"
Cohesion: 0.33
Nodes (3): run(), toggle_dashboard(), toggle_orb()

### Community 109 - "test_vertical_slice_e2e.py"
Cohesion: 0.40
Nodes (3): format_capabilities(), get_system_capabilities(), test_capabilities_endpoint()

### Community 114 - "JARVIS API Contracts & IPC Protocol"
Cohesion: 0.25
Nodes (7): 1. WebSocket Protocol Structure, 2. Command Catalog, 3. Event Catalog, 4. REST Endpoints, Command Envelope (Client -> Server), Event Envelope (Server -> Client), JARVIS API Contracts & IPC Protocol

### Community 116 - "select.jsx"
Cohesion: 0.32
Nodes (7): SelectContent, SelectItem, SelectLabel, SelectScrollDownButton, SelectScrollUpButton, SelectSeparator, SelectTrigger

### Community 117 - "3. Core Subsystems"
Cohesion: 0.25
Nodes (7): 1. High-Level Architectural Topology, 2. Component Directory Boundaries, 3.1. Desktop Windowing & Orb, 3.2. Perception Cascade (Routes 1–4), 3.3. Five-Tier Safety Gate, 3. Core Subsystems, JARVIS System Architecture

### Community 118 - "Phase 3 — Establish Python ↔ Tauri communication"
Cohesion: 0.25
Nodes (5): Communication design, Define command contracts, Define event contracts, Phase 3 — Establish Python ↔ Tauri communication, Process lifecycle

### Community 119 - "Detailed Phase Breakdown"
Cohesion: 0.25
Nodes (7): Detailed Phase Breakdown, JARVIS Project Implementation Progress Tracker, Next Milestone: Milestone 2 — Autonomous AI Desktop Agent (Phases 4–6), Phase 0 — Audit & Stabilize (`5/5 Complete` - 100%), Phase 2 — Native Desktop Application (`7/7 Complete` - 100%), Phase 3 — IPC and Lifecycle (`6/6 Complete` - 100%), Progress Dashboard

### Community 120 - "embla-carousel-react"
Cohesion: 0.11
Nodes (10): embla-carousel-react@8.6.0, @radix-ui/react-label@2.1.4, @radix-ui/react-popover@1.1.11, @radix-ui/react-toggle-group@1.1.7, react@19.0.0, react, embla-carousel-react, @radix-ui/react-label (+2 more)

### Community 123 - "DesktopAdapter"
Cohesion: 0.20
Nodes (4): DesktopSpecialistAgent, DesktopAdapter, Multi-Agent Collaborative System, Table of Contents

### Community 124 - "orb/use-webgl-support.ts"
Cohesion: 0.60
Nodes (5): detect(), getServerSnapshot(), getSnapshot(), subscribe(), useWebGLSupport()

### Community 125 - "default.json"
Cohesion: 0.33
Nodes (5): description, identifier, permissions, $schema, windows

### Community 129 - "Phase 9 — Safety, privacy and security"
Cohesion: 0.40
Nodes (5): Important design principle, Phase 9 — Safety, privacy and security, Privacy gateway, Safety tiers, Security checklist

### Community 130 - "JARVIS — Current State Audit & System Inventory"
Cohesion: 0.40
Nodes (4): 1. Executive Summary, 2. Feature & Component Matrix, 3. Critical Integration Gaps to Resolve in Milestone 1, JARVIS — Current State Audit & System Inventory

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

### Community 143 - "Phase 1 — Refactor the Python engine into a modular backend"
Cohesion: 0.67
Nodes (3): Implementation requirements, Phase 1 — Refactor the Python engine into a modular backend, Proposed structure

## Knowledge Gaps
- **14 isolated node(s):** `jarvis-desktop`, `jarvis-win`, `UIA MTA Worker Thread`, `Nonce-Confirmed Safety Gate`, `Simulated Desktop Environment` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 725 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **71 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JarvisWebSocketService` connect `jarvisStore.ts` to `Detailed Phase Breakdown`?**
  _High betweenness centrality (0.371) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Screen` (e.g. with `1. Snapshot-scoped references instead of bare element marks` and `Phase 1 — reliability contract`) actually correct?**
  _`Screen` has 25 INFERRED edges - model-reasoned connections that need verification._
- **What connects `jarvis-desktop`, `jarvis-win`, `UIA MTA Worker Thread` to the rest of the system?**
  _14 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `compilerOptions` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._
- **Why does `AgentBridge` connect `AgentBridge` to `test_safety.py`, `Safety Gate & Action Denylist`, `schemas.py`, `Usage`, `state_machine.py`, `run_spec`, `Cli Module`, `Detailed Phase Breakdown`, `runner.py`?**
  _High betweenness centrality (0.367) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `ActionResult` (e.g. with `ActionEnvelope` and `ActionError`) actually correct?**
  _`ActionResult` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_safety.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05584192439862543 - nodes in this community are weakly interconnected._