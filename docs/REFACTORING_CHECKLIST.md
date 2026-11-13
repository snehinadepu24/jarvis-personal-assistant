# JARVIS Refactoring Checklist

Use this checklist when continuing the refactoring work.

---

## ✅ Phase 1: Protocol Layer (COMPLETE)

- [x] Create `jarvis/protocol/constants.py` with all magic numbers
- [x] Create `jarvis/protocol/types.py` with type enums
- [x] Create `scripts/generate_types.py` for TypeScript generation
- [x] Generate `apps/desktop/src/types/protocol.ts`
- [x] Update `jarvis/api/schemas.py` to import from protocol
- [x] Update `apps/desktop/src/services/api.ts` to use protocol constants
- [x] Update `apps/desktop/src/services/websocket.ts` to use protocol types
- [x] Test: TypeScript builds without errors
- [x] Test: Python imports work correctly

**Result**: 6 problems fixed, foundation for remaining work established.

---

## ✅ Phase 4: Dead Code Elimination (80% COMPLETE)

### Deleted Files
- [x] `agent/multi_agent/coordinator.py`
- [x] `agent/multi_agent/desktop_specialist.py`
- [x] `agent/multi_agent/memory_specialist.py`
- [x] `agent/multi_agent/safety_reviewer.py`
- [x] `agent/multi_agent/supervisor.py`
- [x] `agent/multi_agent/voice_interaction.py`
- [x] `agent/multi_agent/__init__.py`
- [x] `connectors/browser_cdp.py`
- [x] `connectors/graph.py`
- [x] `connectors/spotify.py`
- [x] `connectors/office_com.py`
- [x] `connectors/system_surfaces.py`
- [x] `connectors/clipboard_safe.py`
- [x] `connectors/windows_manager.py`
- [x] `desktop/startup.py`
- [x] `ui/overlay.py`
- [x] `agent/background_mode.py`
- [x] `cactus_config.py`

### Updated Files
- [x] `capabilities.py` — Removed declarations for deleted connectors
- [x] `safety/risk.py` — Import and use RiskTier from protocol
- [x] `safety/gate.py` — Import and use tier constants from protocol

### Remaining Tasks
- [ ] Delete `AgentDesktopSubprocessAdapter` class from `desktop/adapter.py` (lines 116-197)
- [ ] Inline `get_script_for_goal()` in `agent/common_scripts.py` → caller
- [ ] Inline `est_tokens()` in `llm/base.py` → callers
- [ ] Inline `extract_json()` in `llm/base.py` → callers
- [ ] Remove any remaining imports of deleted modules
- [ ] Test: All tests still pass

**Result**: ~2,500 lines deleted (18% reduction), 4 more problems fixed.

---

## 🔄 Phase 2: Interface Layer (50% COMPLETE)

### Created Files
- [x] `interfaces/perception.py` — IPerceptionBackend, ScreenDiff
- [x] `interfaces/execution.py` — IActionExecutor, ActionResult
- [x] `interfaces/coordination.py` — ICoordinator, TaskOutcome
- [x] `interfaces/__init__.py` — Public API

### Update Callers to Use Interfaces

#### File: `api/bridge.py`
- [ ] Import `from jarvis.interfaces import IPerceptionBackend, IActionExecutor`
- [ ] Change `_execute_task` to accept interface types
- [ ] Remove direct imports of `get_snapshot_manager`, `create_navigation_strategy`
- [ ] Backend/executor creation goes through factories

#### File: `agent/state_machine.py`
- [ ] Import `from jarvis.interfaces import IPerceptionBackend`
- [ ] Remove imports: `choose_route`, `uia_confidence`, `screen_diff`, `serialize_screen`
- [ ] Use `backend.observe()` instead of direct route selection
- [ ] Use `backend.compare(before, after)` instead of `screen_diff()`

#### File: `actions/verify.py`
- [ ] Import `from jarvis.interfaces import IPerceptionBackend`
- [ ] Use `backend.compare()` instead of importing `screen_diff`

### Make Implementations Inherit Interfaces

#### File: `perception/base.py`
- [ ] Make concrete backends implement `IPerceptionBackend`
- [ ] Implement `compare()` method that calls internal `screen_diff()`
- [ ] Encapsulate route selection inside `observe()`

#### File: `actions/uia_executor.py`
- [ ] Make `UiaExecutor` implement `IActionExecutor`
- [ ] Rename `apply()` → `execute()` to match interface
- [ ] Return `ActionResult` from interface, not local class

#### File: `actions/mock_executor.py`
- [ ] Make `MockExecutor` implement `IActionExecutor`
- [ ] Rename `apply()` → `execute()` to match interface
- [ ] Return `ActionResult` from interface, not local class

### Test
- [ ] All imports resolve
- [ ] Type hints work correctly
- [ ] Tests pass
- [ ] No circular imports

**Result**: Will fix 8 coupling problems when complete.

---

## ⏳ Phase 3: Consolidate Executors (NOT STARTED)

### Design
```
BaseExecutor (shared dispatch logic)
    ├─ UiaPrimitives (Windows-specific patterns)
    └─ MockPrimitives (test doubles)
```

### Tasks
- [ ] Create `actions/primitives.py` with `IPrimitives` interface
- [ ] Extract shared dispatch from `UiaExecutor` and `MockExecutor` into `BaseExecutor`
- [ ] Create `actions/uia_primitives.py` with Windows UIA patterns
- [ ] Create `actions/mock_primitives.py` with test implementations
- [ ] Update `UiaExecutor` to use `BaseExecutor(UiaPrimitives())`
- [ ] Update `MockExecutor` to use `BaseExecutor(MockPrimitives())`
- [ ] Delete duplicated dispatch logic
- [ ] Test: All executor tests pass

**Result**: Will eliminate ~500 lines of duplicated logic.

---

## ⏳ Phase 5: Replace Special Cases (NOT STARTED)

### 5A: Platform Abstraction
- [ ] Create `platform/__init__.py` with platform detection
- [ ] Create `platform/windows.py` with Windows implementations
- [ ] Create `platform/mock.py` with cross-platform mocks
- [ ] Replace all `if sys.platform != "win32"` checks with imports from `platform/`
- [ ] Test: Works on Windows and in mock mode

### 5B: Error Taxonomy
- [ ] Create `core/errors.py` with exception hierarchy
- [ ] Define `UIAError`, `ElementNotFoundError`, `PatternNotAvailableError`, etc.
- [ ] Replace `except Exception: pass` with specific error handling
- [ ] Document fallback strategies in error handlers
- [ ] Test: Errors propagate correctly

### 5C: Event-Driven Coordination
- [ ] Create `core/async_utils.py`
- [ ] Implement `wait_for_condition(check, timeout)` helper
- [ ] Replace hardcoded `sleep()` calls with semantic waits
- [ ] Test: UI timing still works correctly

### 5D: Retry Policy Objects
- [ ] Add `RetryPolicy` class to `core/async_utils.py`
- [ ] Replace hardcoded retry counts (2, 3) with policy objects
- [ ] Support exponential backoff, configurable delays
- [ ] Test: Retries work as expected

**Result**: Will fix 17 special case problems.

---

## ⏳ Phase 6: Fix Navigation (NOT STARTED)

### Design
```python
# Navigation returns plans
class NavigationPlan:
    steps: List[NavigationStep]

class NavigationStrategy:
    async def plan_menu_navigation(path, screen) -> NavigationPlan

# Agent executes plans
plan = navigation.plan_menu_navigation(["File", "Open"], screen)
for step in plan.steps:
    result = await executor.execute(step, screen)
```

### Tasks
- [ ] Update `perception/navigation.py` to return `NavigationPlan` objects
- [ ] Remove executor dependency from navigation module
- [ ] Update agent to execute navigation plans
- [ ] Test: Menu navigation still works
- [ ] Test: No circular dependency

**Result**: Will fix circular dependency problem.

---

## 🧪 Testing Checklist

After each phase:

### Unit Tests
- [ ] Run: `python test_all_core_functions.py`
- [ ] All passing tests still pass
- [ ] No new failures introduced

### Integration Tests
- [ ] Run: `python test_phase4_integration.py`
- [ ] Run: `python test_task_flow.py`
- [ ] Task execution works end-to-end

### Frontend Build
- [ ] Run: `cd apps/desktop && npm run build`
- [ ] No TypeScript errors
- [ ] Protocol types imported correctly

### Manual Testing
- [ ] Start backend: `python -m jarvis.cli execute "open notepad"`
- [ ] Task completes successfully
- [ ] No runtime errors in logs

---

## 📝 Documentation Updates

After completing phases:

- [ ] Update `REFACTORING_SUMMARY.md` with progress
- [ ] Update metrics in progress reports
- [ ] Document any new patterns or conventions
- [ ] Update architecture diagrams if structure changed

---

## ⚠️ Common Pitfalls

1. **Circular Imports**: If you get circular import errors:
   - Move shared types to `core/schema.py`
   - Use `from __future__ import annotations` and string type hints
   - Import inside functions if necessary

2. **Breaking Changes**: If tests fail:
   - Check interface contracts match implementations
   - Verify method signatures haven't changed
   - Look for renamed methods (apply → execute)

3. **TypeScript Errors**: If frontend doesn't compile:
   - Re-run `python scripts/generate_types.py`
   - Check imports are from `'../types/protocol'`
   - Clear build cache: `rm -rf dist/`

4. **Missing Imports**: If code can't find modules:
   - Check you deleted the right files
   - Update any remaining imports of deleted modules
   - Search codebase: `git grep "deleted_module_name"`

---

## ✨ Success Criteria

### Phase 1 ✅
- TypeScript types auto-generated from Python
- No hardcoded API URLs in frontend
- All magic numbers have names

### Phase 2 ⏳
- High-level code imports interfaces, not implementations
- Concrete classes implement interface protocols
- No tight coupling between layers

### Phase 3 ⏳
- Executor logic written once in BaseExecutor
- Platform-specific code isolated in primitives
- No duplicated dispatch logic

### Phase 4 ✅
- All dead code deleted
- No unused imports
- Codebase 20% smaller

### Phase 5 ⏳
- No `if sys.platform` checks (use platform module)
- No `except Exception: pass` (use error taxonomy)
- No hardcoded sleeps (use wait_for_condition)

### Phase 6 ⏳
- Navigation module doesn't import executor
- Perception layer is pure observation
- No circular dependencies

---

**Use this checklist to track progress and ensure nothing is missed.**
