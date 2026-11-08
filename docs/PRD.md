# JARVIS for Windows — PRD

## Original problem statement
Build the Windows agent of Project JARVIS as one Python process per the v1.0 build document (28 Oct 2026):
UIA via comtypes on a dedicated MTA thread behind a PerceptionBackend interface, semantic-first perception
cascade (connector → UIA Set-of-Marks → OCR/detector → VLM), element re-resolution by selector chain,
tier 0-4 nonce-confirmed safety gate, prompt-injection defenses, append-only SQLite audit, plain-asyncio
state machine with budgets and loop detection, LLM layer (cloud + local), voice loop, connectors (route 1),
benchmark harness (JARVIS-Win-30 format, arms A–D).

**User choices:** Windows package only (no web dashboard) · planner = Gemini 3.6 Flash via Emergent key ·
demo tasks: Bluetooth toggle, Notepad Save As, Teams draft (no send), injection-resistance check ·
extras: benchmark harness, connectors (route 1), voice loop.

## Architecture
- `/app/jarvis` package; modules map 1:1 to build-doc §4 (core/perception/actions/connectors/agent/llm/voice/safety/ui/bench).
- Windows-only modules import-guard: comtypes UIA backend, UIA executor (with §3.2 selector-chain re-resolution and §6.2-6.4 patterns/SendInput/activation), WinRT OCR, voice, tray/overlay raise ImportError off-Windows.
- `SimulatedDesktop` (`perception/mock_backend.py`) is the executable spec of the Windows desktop so the whole agent core is verifiable on any OS.
- Planner: gemini-3.6-flash via emergentintegrations (EMERGENT_LLM_KEY), Step-validated JSON; scripted + skill replay planners for 0-LLM runs; Ollama/llama.cpp clients included.
- MCP: mcp 2.3.0 v2 client (ClientSession/stdio_client/discover), servers from jarvis.toml [mcp_servers], unknown tools tier 3, per-tool tier overrides [mcp_tiers]; McpToolRegistry feeds route-1 matching in the state machine.
- Safety: risk tiers (§11), nonce gate (tier-3 popup with spoken summary + 2 s cancel window + timed nonce prompt, tier-4 typed nonce, hash-bound), redaction, injection scanner, deny-list, SQLite WAL audit (14 columns per §11).

## Implemented (2026-06-14)
- Full package per §4; CLI: `dump / run / bench / smoke / mcp / skill-replay / voice / setup-check`; 59 pytest tests.
- Demo tasks with real checkers: Bluetooth toggle (tier 2, element_state + mock_state checkers), Notepad Save As (real file; overwrite → confirm dialog → ask_user), Teams draft (Send never invoked), injection-resistance (no tier ≥3 action, 0 bytes off-device).
- Skills: any successful run (scripted or live Gemini) recorded via `--record-skill` into selector-based YAML; replays with 0 LLM calls; arm D does record-on-seed-0/replay-after automatically.
- Benchmark runner arms A/B/D on the simulator (arm C requires real Windows + VLM), metrics per §14 with 3-seed determinism.
- Live-verified: gemini-3.6-flash planned the Bluetooth task (3 steps, checker PASS); its recorded skill replayed with llm_calls=0 and checker PASS.

## Verified
- 59/59 pytest (schema/serialize/diff/router, safety tiers/gate/redaction/injection/denylist/audit, gate 2 s-cancel + timed nonce UX, state machine e2e ×4, loop/budgets, files/powershell/spotify/skills, MCP client against a real stdio fixture server, live LLM test).
- CLI: smoke PASS (mock), run ×4 tasks, record-skill → skill-replay (0 LLM), mcp list, bench A/B/D 1.00 checker success + determinism.
- Tier-3 denial: click on Send gated → denied → audit row `approved_by=denied`, Send never invoked.

## Not executed here (needs the user's Windows 11 machine)
Real UIA snapshot timing (`jarvis smoke` on Windows targets the <300 ms p50 acceptance), real Settings toggle, WinRT OCR, voice latency, overlay/tray, Graph/COM/CDP/Spotify live flows, arm C.

## Backlog
- P0: Run `jarvis smoke` on the real Windows 11 box (week-1/2 acceptance, 10/10).
- P1: JARVIS-Win-30 full 30-task suite + arm C on-device; skill recording of multi-app Gemini runs.
- P2: Dashboard UI (user deferred), MSIX/signing, JEA PowerShell profile.
