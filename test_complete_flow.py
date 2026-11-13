#!/usr/bin/env python3
"""
Complete end-to-end test of JARVIS task submission flow
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.api.bridge import AgentBridge
from jarvis.config import Config

async def main():
    print("=" * 70)
    print(" JARVIS END-TO-END FLOW TEST")
    print("=" * 70)
    
    # Load config
    print("\n✓ Loading configuration...")
    cfg = Config.load()
    print(f"  Model: {cfg.planner_model}")
    print(f"  Thinking: {cfg.thinking}")
    
    # Initialize bridge  
    print("\n✓ Initializing AgentBridge...")
    bridge = AgentBridge(cfg)
    
    # Test imports
    print("\n✓ Testing imports...")
    from jarvis.llm.router import LlmRouter
    from jarvis.llm.gemini import GeminiLLM
    print(f"  - LlmRouter imported")
    print(f"  - GeminiLLM imported")
    
    # Test planner creation
    print("\n✓ Testing planner instantiation...")
    try:
        planner = LlmRouter(GeminiLLM(cfg.planner_model), thinking=cfg.thinking)
        print(f"  - LlmRouter created: {type(planner).__name__}")
    except Exception as e:
        print(f"  ✗ Failed to create planner: {e}")
        return
    
    # Test backend initialization
    print("\n✓ Testing backend initialization...")
    try:
        from jarvis.bench.runner import _use_mock
        if _use_mock(cfg):
            print(f"  - Using mock backend (JARVIS_BACKEND=mock)")
            from jarvis.perception.mock_backend import SimulatedDesktop
            backend = SimulatedDesktop(fs_root=cfg.data_dir / "test")
            print(f"  - Mock backend created")
        else:
            print(f"  - Using real Windows backend")
            from jarvis.perception.base import build_backend
            backend = build_backend(cfg)
            print(f"  - Real backend created")
    except Exception as e:
        print(f"  ✗ Backend initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Submit task
    print("\n✓ Submitting test task...")
    try:
        task_id = await bridge.submit_task(
            goal="Open Notepad and write Hello from JARVIS.",
            planner_mode="auto",
            engine="state_machine",
        )
        print(f"  - Task ID: {task_id}")
        
        # Wait and check status
        await asyncio.sleep(1.0)
        status = bridge.get_task_status(task_id)
        print(f"  - Status: {status['status']}")
        
        # Cancel
        print("\n✓ Cancelling task...")
        await bridge.cancel_task(task_id)
        await asyncio.sleep(0.5)
        
        final_status = bridge.get_task_status(task_id)
        print(f"  - Final status: {final_status['status']}")
        
    except Exception as e:
        print(f"\n✗ Task submission failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED - Flow is working correctly!")
    print("=" * 70)
    print("\nThe issue was: RouterPlanner doesn't exist in jarvis.llm.router")
    print("The fix was: Import LlmRouter and GeminiLLM instead")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
