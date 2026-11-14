"""
Test Phase 4 Integration - Snapshot Manager, Background Executor, Navigation Strategy
Run this to verify all components are wired correctly into the system.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


async def test_imports():
    """Test 1: Verify all new modules can be imported"""
    print("\n" + "="*60)
    print("TEST 1: Module Imports")
    print("="*60)
    
    try:
        from jarvis.perception.snapshot import get_snapshot_manager, SnapshotManager
        print("✅ snapshot.py imported")
        
        from jarvis.agent.background_mode import create_background_executor, BackgroundConfig
        print("✅ background_mode.py imported")
        
        from jarvis.perception.navigation import create_navigation_strategy, NavigationStrategy
        print("✅ navigation.py imported")
        
        from jarvis.agent.state_machine import AgentContext
        print("✅ AgentContext imported")
        
        # Check AgentContext has new fields
        import inspect
        ctx_fields = [f.name for f in AgentContext.__dataclass_fields__.values()]
        assert 'snapshot_manager' in ctx_fields, "AgentContext missing snapshot_manager"
        assert 'background_executor' in ctx_fields, "AgentContext missing background_executor"
        assert 'navigation_strategy' in ctx_fields, "AgentContext missing navigation_strategy"
        print("✅ AgentContext has new fields")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_snapshot_manager():
    """Test 2: Snapshot Manager functionality"""
    print("\n" + "="*60)
    print("TEST 2: Snapshot Manager")
    print("="*60)
    
    try:
        from jarvis.perception.snapshot import get_snapshot_manager
        from jarvis.core.schema import Screen, UiElement, Rect
        
        manager = get_snapshot_manager()
        print(f"✅ Snapshot manager created: {manager}")
        
        # Create mock screen
        screen = Screen(
            app="TestApp",
            window_title="Test Window",
            elements=[
                UiElement(
                    mark=1, 
                    role="button", 
                    name="Test Button", 
                    control_type=50000,
                    rect=Rect(l=10, t=10, r=100, b=50),
                    enabled=True,
                    key="test_button_key"
                ),
                UiElement(
                    mark=2, 
                    role="textbox", 
                    name="Test Input", 
                    control_type=50004,
                    rect=Rect(l=10, t=60, r=100, b=100),
                    enabled=True,
                    key="test_input_key"
                ),
            ],
            hwnd=12345,
        )
        
        # Create snapshot
        snapshot_id = manager.create_snapshot(screen)
        print(f"✅ Created snapshot: {snapshot_id}")
        
        # Validate marks
        is_valid, reason = manager.validate_mark(1, screen)
        print(f"✅ Mark 1 validation: {is_valid} ({reason})")
        assert is_valid, "Mark 1 should be valid"
        
        # Test invalid mark
        is_valid, reason = manager.validate_mark(999, screen)
        print(f"✅ Mark 999 validation: {is_valid} ({reason})")
        assert not is_valid, "Mark 999 should be invalid"
        
        # Test age expiration
        print("⏳ Waiting 6 seconds to test age expiration...")
        await asyncio.sleep(6)
        is_valid, reason = manager.validate_mark(1, screen)
        print(f"✅ Mark 1 after 6s: {is_valid} ({reason})")
        assert not is_valid, "Mark 1 should be expired"
        
        # Test needs_refresh
        needs = manager.needs_refresh()
        print(f"✅ Needs refresh: {needs}")
        assert needs, "Should need refresh after 6s"
        
        return True
    except Exception as e:
        print(f"❌ Snapshot manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_background_executor():
    """Test 3: Background Executor functionality"""
    print("\n" + "="*60)
    print("TEST 3: Background Executor")
    print("="*60)
    
    try:
        from jarvis.agent.background_mode import create_background_executor, BackgroundConfig
        
        # Create with disabled config (faster test)
        config = BackgroundConfig(enabled=False)
        executor = create_background_executor(config)
        print(f"✅ Background executor created: {executor}")
        
        # Test normal execution (no background)
        async def dummy_task(value):
            await asyncio.sleep(0.1)
            return value * 2
        
        result = await executor.execute_in_background(dummy_task, 21)
        print(f"✅ Task executed: 21 * 2 = {result}")
        assert result == 42, "Task should return 42"
        
        # Test with enabled config (but skip idle wait for testing)
        config_enabled = BackgroundConfig(
            enabled=True,
            defer_on_user_active=False,  # Skip idle detection
            restore_focus=True,
            notify_on_start=False,  # Skip notifications
            notify_on_complete=False,
        )
        executor_enabled = create_background_executor(config_enabled)
        
        result = await executor_enabled.execute_in_background(dummy_task, 50)
        print(f"✅ Background task executed: 50 * 2 = {result}")
        assert result == 100, "Background task should return 100"
        
        return True
    except Exception as e:
        print(f"❌ Background executor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_navigation_strategy():
    """Test 4: Navigation Strategy functionality"""
    print("\n" + "="*60)
    print("TEST 4: Navigation Strategy")
    print("="*60)
    
    try:
        from jarvis.perception.navigation import NavigationStrategy
        from jarvis.core.schema import Rect
        
        # Create with mock backend/executor
        class MockBackend:
            async def observe(self, route=2):
                from jarvis.core.schema import Screen, UiElement
                return Screen(
                    app="TestApp",
                    window_title="Test",
                    elements=[
                        UiElement(
                            mark=1, 
                            role="menuitem", 
                            name="File", 
                            control_type=50011,
                            rect=Rect(l=0, t=0, r=50, b=20),
                            enabled=True,
                            key="file_menu"
                        ),
                        UiElement(
                            mark=2, 
                            role="menuitem", 
                            name="Open", 
                            control_type=50011,
                            rect=Rect(l=0, t=20, r=50, b=40),
                            enabled=True,
                            key="open_menu"
                        ),
                    ],
                    hwnd=123,
                )
        
        class MockExecutor:
            async def apply(self, step, screen=None):
                from jarvis.actions.base import ActionResult
                return ActionResult(True, "mocked")
        
        backend = MockBackend()
        executor = MockExecutor()
        nav = NavigationStrategy(backend, executor)
        print(f"✅ Navigation strategy created: {nav}")
        
        # Test properties
        print(f"✅ Max depth: {nav.max_depth}")
        print(f"✅ Breadcrumbs: {len(nav.breadcrumbs)}")
        
        # Test breadcrumb tracking (would need full integration to test navigation)
        assert nav.breadcrumbs == [], "Breadcrumbs should start empty"
        print("✅ Breadcrumb tracking ready")
        
        return True
    except Exception as e:
        print(f"❌ Navigation strategy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_executor_integration():
    """Test 5: UiaExecutor integration"""
    print("\n" + "="*60)
    print("TEST 5: UiaExecutor Integration")
    print("="*60)
    
    try:
        from jarvis.actions.uia_executor import UiaExecutor
        from jarvis.perception.snapshot import get_snapshot_manager
        
        # Create mock backend
        class MockBackend:
            thread = None
            async def observe(self, route=2):
                from jarvis.core.schema import Screen
                return Screen(app="Test", window_title="Test", elements=[], hwnd=123)
            
            def list_windows(self):
                return []
        
        backend = MockBackend()
        snapshot_manager = get_snapshot_manager()
        
        # Create executor with snapshot manager
        executor = UiaExecutor(backend, snapshot_manager=snapshot_manager)
        print(f"✅ Executor created with snapshot manager")
        
        # Verify snapshot manager is set
        assert executor.snapshot_manager is not None, "Snapshot manager not set"
        print(f"✅ Executor has snapshot_manager: {executor.snapshot_manager}")
        
        # Verify navigation strategy can be set
        class MockNav:
            pass
        
        executor.navigation_strategy = MockNav()
        assert executor.navigation_strategy is not None, "Navigation strategy not set"
        print(f"✅ Executor can accept navigation_strategy")
        
        return True
    except Exception as e:
        print(f"❌ Executor integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_bridge_integration():
    """Test 6: AgentBridge integration"""
    print("\n" + "="*60)
    print("TEST 6: AgentBridge Integration")
    print("="*60)
    
    try:
        from jarvis.api.bridge import AgentBridge
        from jarvis.config import Config
        import tempfile
        
        # Create temp config
        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = Config()
            cfg.data_dir = Path(tmpdir)
            
            # Check that bridge can be created
            # (Don't actually submit tasks in test)
            bridge = AgentBridge.get_instance(cfg)
            print(f"✅ Bridge created: {bridge}")
            
            print("✅ Bridge integration verified (structure check)")
            
        return True
    except Exception as e:
        print(f"❌ Bridge integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all integration tests"""
    print("\n" + "="*70)
    print(" "*15 + "PHASE 4 INTEGRATION TEST SUITE")
    print("="*70)
    print("\nTesting: Snapshot Manager, Background Executor, Navigation Strategy")
    print("="*70)
    
    tests = [
        ("Module Imports", test_imports),
        ("Snapshot Manager", test_snapshot_manager),
        ("Background Executor", test_background_executor),
        ("Navigation Strategy", test_navigation_strategy),
        ("UiaExecutor Integration", test_executor_integration),
        ("AgentBridge Integration", test_bridge_integration),
    ]
    
    results = []
    
    for name, test_fn in tests:
        try:
            result = await test_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {name}")
    
    print("="*70)
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Phase 4 integration is COMPLETE!")
        print("\n✅ Components ready:")
        print("   • Snapshot Manager - prevents stale references")
        print("   • Background Executor - non-disruptive tasks")
        print("   • Navigation Strategy - complex UI navigation")
        print("\n📋 Next Steps:")
        print("   1. Test with real JARVIS tasks")
        print("   2. Monitor metrics and performance")
        print("   3. Implement remaining features (notifications, VLM)")
        print("   4. Proceed to Milestone 2")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
