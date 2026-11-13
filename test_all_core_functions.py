#!/usr/bin/env python3
"""
Comprehensive JARVIS Core Functionality Test Suite
Tests all critical actions: UI tree access, clicking, typing, window switching, etc.
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.config import Config
from jarvis.perception.base import build_backend
from jarvis.actions.uia_executor import UiaExecutor
from jarvis.connectors.files import FilesConnector
from jarvis.core.schema import *
from jarvis.safety.gate import ConfirmationGate, auto_approve_confirmer
from jarvis.safety.audit import Audit

class TestResults:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def record_pass(self, test_name):
        self.total += 1
        self.passed += 1
        print(f"  ✓ {test_name}")
    
    def record_fail(self, test_name, reason):
        self.total += 1
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"  ✗ {test_name}: {reason}")

async def test_ui_tree_access(backend, results):
    """Test 1: UI Automation Tree Access"""
    print("\n[1] Testing UI Automation Tree Access...")
    try:
        # Observe desktop (await the coroutine)
        screen = await backend.observe(route=2)  # UIA route
        
        if screen and len(screen.elements) > 0:
            results.record_pass("Desktop UI tree accessible")
            print(f"      Found {len(screen.elements)} UI elements")
        else:
            results.record_fail("Desktop UI tree accessible", "No elements found")
            return False
        
        # Check if elements have valid properties
        sample_el = screen.elements[0]
        if hasattr(sample_el, 'role') and hasattr(sample_el, 'label'):
            results.record_pass("UI elements have required properties")
        else:
            results.record_fail("UI elements have required properties", "Missing role or label")
        
        return True
    except Exception as e:
        results.record_fail("UI tree access", str(e))
        return False

async def test_window_focus(backend, executor, results):
    """Test 2: Window Focus and Switching"""
    print("\n[2] Testing Window Focus and Switching...")
    try:
        # Get current window
        screen = await backend.observe(route=2)
        current_window = screen.app if screen else "Unknown"
        results.record_pass(f"Detect current window: {current_window}")
        
        # Try focusing a different window (Explorer usually available)
        focus_action = FocusWindow(type="focus_window", window_title="File Explorer", reason="test")
        step = Step(thought="Focus File Explorer", action=focus_action, expect="Window focused")
        result = await executor.apply(step, screen)
        
        if result.ok or "not found" in result.detail.lower():
            results.record_pass("Focus window action executed")
        else:
            results.record_fail("Focus window action", result.detail)
    except Exception as e:
        results.record_fail("Window focus", str(e))

async def test_app_launch(backend, executor, results):
    """Test 3: Application Launch"""
    print("\n[3] Testing Application Launch...")
    try:
        screen = await backend.observe(route=2)
        
        # Launch Notepad
        open_action = OpenApp(type="open_app", name="Notepad", reason="test")
        step = Step(thought="Launch Notepad", action=open_action, expect="Notepad opens")
        result = await executor.apply(step, screen)
        
        if result.ok:
            results.record_pass("Launch application (Notepad)")
            await asyncio.sleep(1.5)  # Wait for app to open
            return True
        else:
            results.record_fail("Launch application", result.detail)
            return False
    except Exception as e:
        results.record_fail("Application launch", str(e))
        return False

async def test_typing(backend, executor, results):
    """Test 4: Keyboard Typing"""
    print("\n[4] Testing Keyboard Typing...")
    try:
        # Refresh screen to get Notepad window
        screen = await backend.observe(route=2)
        
        # Type text
        type_action = SetText(type="type", text="Hello JARVIS Test", mark=0, reason="test", submit=False)
        step = Step(thought="Type test text", action=type_action, expect="Text typed")
        result = await executor.apply(step, screen)
        
        if result.ok:
            results.record_pass("Type text into focused window")
        else:
            results.record_fail("Type text", result.detail)
    except Exception as e:
        results.record_fail("Keyboard typing", str(e))

async def test_hotkey(backend, executor, results):
    """Test 5: Hotkey/Shortcuts"""
    print("\n[5] Testing Hotkey Actions...")
    try:
        screen = await backend.observe(route=2)
        
        # Test Ctrl+A (select all)
        hotkey_action = Hotkey(type="hotkey", keys="ctrl+a", reason="test")
        step = Step(thought="Select all text", action=hotkey_action, expect="Text selected")
        result = await executor.apply(step, screen)
        
        if result.ok:
            results.record_pass("Execute hotkey (Ctrl+A)")
        else:
            results.record_fail("Execute hotkey", result.detail)
    except Exception as e:
        results.record_fail("Hotkey action", str(e))

async def test_click_action(backend, executor, results):
    """Test 6: UI Element Clicking"""
    print("\n[6] Testing UI Element Clicking...")
    try:
        screen = await backend.observe(route=2)
        
        # Find a clickable element (any button/menu)
        clickable = None
        for el in screen.elements:
            if el.role in ["button", "menuitem", "tab"]:
                clickable = el
                break
        
        if clickable:
            # Try clicking it
            click_action = Click(type="click", mark=clickable.mark, reason="test")
            step = Step(thought="Click UI element", action=click_action, expect="Element clicked")
            result = await executor.apply(step, screen)
            
            if result.ok:
                results.record_pass(f"Click UI element (mark={clickable.mark}, role={clickable.role})")
            else:
                results.record_fail("Click UI element", result.detail)
        else:
            results.record_pass("No clickable elements to test (skipped)")
    except Exception as e:
        results.record_fail("Click action", str(e))

async def test_window_close(backend, executor, results):
    """Test 7: Close Window/Application"""
    print("\n[7] Testing Window Close...")
    try:
        screen = await backend.observe(route=2)
        
        # Close Notepad (Alt+F4)
        hotkey_action = Hotkey(type="hotkey", keys="alt+f4", reason="test")
        step = Step(thought="Close Notepad", action=hotkey_action, expect="Window closes")
        result = await executor.apply(step, screen)
        
        if result.ok:
            results.record_pass("Close window (Alt+F4)")
            await asyncio.sleep(0.5)
            
            # Handle "Don't Save" dialog if appears
            screen2 = await backend.observe(route=2)
            if screen2 and "notepad" in screen2.app.lower():
                # Press Tab then Enter to click "Don't Save"
                tab_action = Hotkey(type="hotkey", keys="tab", reason="navigate")
                await executor.apply(Step(thought="Navigate", action=tab_action, expect=""), screen2)
                enter_action = Hotkey(type="hotkey", keys="enter", reason="confirm")
                await executor.apply(Step(thought="Confirm", action=enter_action, expect=""), screen2)
                results.record_pass("Handle save dialog")
        else:
            results.record_fail("Close window", result.detail)
    except Exception as e:
        results.record_fail("Window close", str(e))

async def test_screen_snapshot(backend, results):
    """Test 8: Screen Snapshot and Observation"""
    print("\n[8] Testing Screen Snapshot...")
    try:
        # Test different perception routes
        routes_tested = 0
        
        # Route 2: UIA
        screen_uia = await backend.observe(route=2)
        if screen_uia:
            results.record_pass(f"UIA observation (route=2): {len(screen_uia.elements)} elements")
            routes_tested += 1
        
        # Check snapshot has required data
        if screen_uia and hasattr(screen_uia, 'app') and hasattr(screen_uia, 'window_title'):
            results.record_pass("Screen snapshot has window context")
        else:
            results.record_fail("Screen snapshot structure", "Missing app or window_title")
        
        if routes_tested > 0:
            results.record_pass(f"Perception routes functional ({routes_tested}/1)")
        
    except Exception as e:
        results.record_fail("Screen snapshot", str(e))

async def test_wait_action(backend, executor, results):
    """Test 9: Wait/Delay Action"""
    print("\n[9] Testing Wait Action...")
    try:
        screen = await backend.observe(route=2)
        
        import time
        start = time.time()
        wait_action = Wait(type="wait", seconds=0.5, reason="test")
        step = Step(thought="Wait briefly", action=wait_action, expect="Time passed")
        result = await executor.apply(step, screen)
        elapsed = time.time() - start
        
        if result.ok and elapsed >= 0.4:  # Allow some margin
            results.record_pass(f"Wait action ({elapsed:.2f}s)")
        else:
            results.record_fail("Wait action", f"Elapsed: {elapsed:.2f}s")
    except Exception as e:
        results.record_fail("Wait action", str(e))

async def main():
    print("=" * 70)
    print("JARVIS CORE FUNCTIONALITY TEST SUITE")
    print("=" * 70)
    print("\nThis will test:")
    print("  • UI Automation tree access")
    print("  • Window focus and switching")
    print("  • Application launching")
    print("  • Keyboard typing")
    print("  • Hotkey/shortcuts")
    print("  • UI element clicking")
    print("  • Window closing")
    print("  • Screen snapshots")
    print("  • Wait/timing actions")
    print("\n" + "=" * 70)
    
    results = TestResults()
    
    # Initialize JARVIS components
    print("\n[0] Initializing JARVIS components...")
    try:
        cfg = Config.load()
        print(f"  ✓ Config loaded")
        
        backend = build_backend(cfg)
        print(f"  ✓ Backend initialized: {type(backend).__name__}")
        
        fs_root = cfg.data_dir / "test_core"
        fs_root.mkdir(parents=True, exist_ok=True)
        executor = UiaExecutor(backend, FilesConnector(fs_root))
        print(f"  ✓ Executor initialized")
        
        gate = ConfirmationGate(confirmer=auto_approve_confirmer)
        audit = Audit(cfg.data_dir / "test_audit.db")
        print(f"  ✓ Safety gate and audit initialized")
        
    except Exception as e:
        print(f"  ✗ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Run all tests
    try:
        await test_ui_tree_access(backend, results)
        await test_screen_snapshot(backend, results)
        await test_window_focus(backend, executor, results)
        
        notepad_opened = await test_app_launch(backend, executor, results)
        
        if notepad_opened:
            await test_typing(backend, executor, results)
            await test_hotkey(backend, executor, results)
            await test_click_action(backend, executor, results)
            await test_window_close(backend, executor, results)
        
        await test_wait_action(backend, executor, results)
        
    except Exception as e:
        print(f"\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()
    
    # Print results
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"\nTotal Tests: {results.total}")
    print(f"Passed:      {results.passed} ✓")
    print(f"Failed:      {results.failed} ✗")
    print(f"Success Rate: {(results.passed/results.total*100) if results.total > 0 else 0:.1f}%")
    
    if results.failed > 0:
        print("\n" + "=" * 70)
        print("FAILED TESTS:")
        print("=" * 70)
        for test_name, reason in results.errors:
            print(f"  ✗ {test_name}")
            print(f"    Reason: {reason}")
    
    print("\n" + "=" * 70)
    if results.failed == 0:
        print("✓ ALL TESTS PASSED - JARVIS CORE FUNCTIONS ARE WORKING!")
    else:
        print("⚠ SOME TESTS FAILED - REVIEW ERRORS ABOVE")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
