# JARVIS vs. Vercel `agent-desktop`

Reference repository: <https://github.com/vercel-labs/agent-desktop>  
Reviewed: 2026-11-03

## Executive conclusion

No, `agent-desktop` is not the same product as our JARVIS project.

They overlap in the ability to inspect and operate desktop applications, but they
solve different layers of the problem:

| Area | Vercel `agent-desktop` | Our JARVIS |
|---|---|---|
| Primary role | Cross-platform desktop-control CLI and C FFI | Windows voice-first autonomous agent |
| Perception | Accessibility-tree snapshots with action refs | UIA-first perception cascade: connector, UIA, OCR/detector, optional VLM |
| Planning | The calling agent owns the observe/act/verify loop | Gemini/local/scripted planners plus an asyncio state machine |
| Interaction | JSON CLI commands, headless by default | Python action executor, voice, tray, orb, and CLI |
| Safety | Headless/headed distinction, stale refs, structured errors | Tier 0-4 risk gate, nonce confirmation, injection defenses, deny-list, audit |
| Platforms | macOS, Windows, Linux | Windows-first, simulated desktop for non-Windows development |
| Packaging | npm/native binaries and a C FFI | Python package with Windows extras |
| Scope | Desktop surfaces, windows, clipboard, notifications, input | Desktop tasks plus voice, LLM routing, skills, connectors, benchmarks, audit |

The best direction is to keep JARVIS as the product and adopt `agent-desktop`-style
contracts and capabilities where they make JARVIS more reliable.

## Important ideas to take from `agent-desktop`

### 1. Snapshot-scoped references instead of bare element marks

`agent-desktop` returns a `snapshot_id` and a unique ref for every actionable
element, for example `@s8f3k2p9:e8`. The ref belongs to that snapshot. If the UI
changes, the tool returns `STALE_REF` or `AMBIGUOUS_TARGET` and the agent must
observe again.

Our current schema has integer marks and selector chains
([jarvis/jarvis/core/schema.py](jarvis/jarvis/core/schema.py)), but it does not
make the observation generation explicit in every action target.

**Adopt:**

- Add an observation/snapshot ID to `Screen`.
- Include the snapshot ID in action targets.
- Reject actions whose target came from an old snapshot.
- Re-observe and re-plan on stale or ambiguous targets.
- Keep selector-chain re-resolution as the recovery mechanism after a fresh
  snapshot, rather than trusting a numeric mark.

This should reduce accidental actions against a changed window and make failures
explainable.

### 2. A stable JSON envelope for every tool operation

The reference CLI emits one predictable envelope per command:

```json
{
  "version": "2.6",
  "ok": true,
  "command": "snapshot",
  "data": {}
}
```

Failures use structured fields such as `code`, `disposition`, and `suggestion`.
This is stronger than returning inconsistent strings from individual connectors.

**Adopt for JARVIS connectors and executors:**

```json
{
  "version": "1",
  "ok": false,
  "command": "click",
  "error": {
    "code": "STALE_TARGET",
    "disposition": { "retry": true, "requires_observe": true },
    "suggestion": "Take a fresh UIA snapshot and retry with its target ref."
  }
}
```

Define a small, shared error vocabulary: `INVALID_ARGS`, `NOT_FOUND`,
`STALE_TARGET`, `AMBIGUOUS_TARGET`, `PERMISSION_DENIED`, `UNSUPPORTED`,
`TIMEOUT`, `ACTION_FAILED`, and `SAFETY_BLOCKED`.

The state machine should retry only when the error explicitly says retry is safe.
This complements the existing loop detector and budgets in
[jarvis/jarvis/agent/state_machine.py](jarvis/jarvis/agent/state_machine.py).

### 3. Headless should be the default

`agent-desktop` prefers accessibility APIs without moving the pointer or taking
focus. Physical input is opt-in through `--headed`.

JARVIS already has a semantic UIA executor, but the same policy should be made
explicit:

- Prefer UIA patterns, window messages, and semantic controls.
- Do not activate or steal focus for ordinary actions.
- Use mouse/keyboard simulation only as a declared fallback.
- Require a higher safety tier for physical input, clipboard writes, and
  foreground activation.
- Audit whether an action used semantic or physical input.

This is especially important for destructive or externally visible tasks.

### 4. Dense screens need two-stage observation

The reference uses a compact skeleton snapshot first, then drills into a subtree
with a root ref. This avoids sending an entire dense app tree to the planner.

**Add to the perception cascade:**

1. Capture a compact window/surface outline.
2. Select the relevant subtree or region.
3. Capture detailed interactive elements only in that subtree.
4. Plan against the detailed snapshot.

This fits our existing route selection and screen serialization
([jarvis/jarvis/perception/serialize.py](jarvis/jarvis/perception/serialize.py))
and should lower token use and improve target accuracy.

### 5. Broader desktop surface coverage

The reference has first-class operations for:

- App/window listing and launch
- Focus, resize, move, minimize, maximize, and restore
- Clipboard get/set/clear
- Notifications and notification actions
- System surfaces such as taskbar, tray, Start menu, and Action Center
- Batch operations
- Screenshots and cursor overlays
- Session and trace/debug commands

JARVIS has strong task-specific connectors and a Windows UIA layer, but these
capabilities should be added behind typed connectors rather than as ad-hoc
planner actions. Recommended priority:

1. System surfaces and window management
2. Clipboard with sensitivity redaction
3. Notifications
4. Batch execution with per-step results
5. Trace/debug artifact export

Every new capability must go through the existing risk classifier and audit
database, not bypass the gate.

### 6. Capability discovery should be built in

`agent-desktop skills get desktop` and `skills get platform` expose version-matched
operating instructions and platform limitations.

JARVIS should expose a machine-readable capability command, for example:

```text
jarvis capabilities --json
```

It should report available perception routes, connectors, voice engines,
permissions, platform limitations, and whether physical input is enabled. The
planner can then avoid proposing unsupported actions instead of discovering the
limitation after execution.

### 7. Make the observe-act-verify contract explicit

The reference documentation strongly reinforces this loop:

```text
observe -> act on a current ref -> observe again -> verify
```

Our state machine already implements
`INTERPRET -> ROUTE -> OBSERVE -> DECIDE -> GATE -> ACT -> VERIFY`
([jarvis/jarvis/agent/state_machine.py](jarvis/jarvis/agent/state_machine.py)).
The improvement is to make the contract visible in the action schema and audit
records:

- observation ID used for planning
- target ref used for execution
- whether the ref was re-resolved
- post-action observation ID
- verification result and evidence
- retry disposition

### 8. Separate the desktop adapter from the planner

`agent-desktop` is deliberately a control adapter; the calling AI owns the loop.
That separation is useful even if we do not depend on the project directly.

Recommended JARVIS boundaries:

- `DesktopAdapter`: observe, find, inspect, act, window/system operations
- `Planner`: intent and next-step planning
- `Safety`: classify, approve/deny, redact, audit
- `Orchestrator`: budgets, retries, loop detection, verification
- `Voice/UI`: input and user feedback only

This keeps a future adapter integration optional and makes the simulated backend
remain a faithful executable specification.

## Recommended implementation plan

### Phase 1 — reliability contract

- Add `snapshot_id` and snapshot timestamps to `Screen`.
- Add snapshot-bound target refs to `Step` actions.
- Add `STALE_TARGET` and `AMBIGUOUS_TARGET` handling.
- Standardize executor/connector JSON result envelopes.
- Record semantic versus physical input in the audit schema.
- Add tests for stale refs, ambiguous windows, and safe retry behavior.

### Phase 2 — perception and capability improvements

- Implement compact skeleton snapshots and subtree detail snapshots.
- Add `jarvis capabilities --json`.
- Add window listing/focus/resize/minimize/restore connectors.
- Add safe clipboard operations with redaction and tier classification.
- Add system-surface discovery for taskbar, tray, Start menu, and Action Center.

### Phase 3 — operations and developer experience

- Add typed batch execution with independent step results.
- Add trace export containing redacted observations, actions, and verification.
- Add a `jarvis desktop-adapter` interface so an external native adapter can be
  plugged in without replacing the JARVIS planner or safety system.
- Document Windows integrity-level limitations and permissions in setup checks.

## What not to copy blindly

- Do not replace the JARVIS safety gate with a headed/headless flag. Headless
  prevents focus/input side effects, but it does not replace risk classification,
  nonce confirmation, prompt-injection defense, or auditability.
- Do not replace the existing UIA backend immediately. JARVIS already has a
  Windows-specific UIA implementation and a simulator; first add a compatibility
  adapter and compare behavior through tests.
- Do not send raw snapshots, screenshots, clipboard contents, or debug artifacts
  to logs or external models without the existing redaction and privacy policy.
- Do not add cross-platform support until the Windows acceptance suite is stable.
- Do not make every command retryable. Retry only explicit transient failures
  after a fresh observation and within the existing budgets.

## Optional integration decision

The lowest-risk integration is an optional adapter, not a rewrite:

1. Keep JARVIS’s Gemini/local planner, voice host, orb, safety gate, audit, and
   benchmark harness.
2. Define a typed `DesktopAdapter` protocol matching the observe/find/act contract.
3. Implement the current UIA backend against that protocol.
4. Optionally add an `agent-desktop` subprocess adapter for experiments and
   cross-platform support.
5. Compare both adapters on the same simulated and real acceptance tasks.

Only make the external adapter the default if it passes the same safety,
determinism, latency, and checker requirements as the current implementation.

## Sources

- [`agent-desktop` README](https://github.com/vercel-labs/agent-desktop/blob/main/README.md)
- [`agent-desktop` installation and platform notes](https://github.com/vercel-labs/agent-desktop/blob/main/docs/install.md)
- [JARVIS project README](jarvis/README.md)
- [JARVIS PRD](memory/PRD.md)
- [JARVIS action and screen schema](jarvis/jarvis/core/schema.py)
- [JARVIS state machine](jarvis/jarvis/agent/state_machine.py)
- [JARVIS confirmation gate](jarvis/jarvis/safety/gate.py)

