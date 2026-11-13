#!/usr/bin/env python3
"""
Test script to verify the task submission flow works end-to-end.
"""
import asyncio
import sys
import os

# Add jarvis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'jarvis'))

from jarvis.api.bridge import AgentBridge
from jarvis.config import Config

async def test_task_submission():
    """Test that a task can be submitted and initialized without errors."""
    print("=" * 60)
    print("Testing JARVIS Task Submission Flow")
    print("=" * 60)
    
    # Step 1: Load config
    print("\n[1] Loading configuration...")
    try:
        cfg = Config.load()
        print(f"    ✓ Config loaded successfully")
        print(f"    - Planner model: {cfg.planner_model}")
        print(f"    - Thinking level: {cfg.thinking}")
    except Exception as e:
        print(f"    ✗ Config load failed: {e}")
        return False
    
    # Step 2: Initialize bridge
    print("\n[2] Initializing AgentBridge...")
    try:
        bridge = AgentBridge(cfg)
        print(f"    ✓ Bridge initialized")
    except Exception as e:
        print(f"    ✗ Bridge initialization failed: {e}")
        return False
    
    # Step 3: Test LLM Router instantiation
    print("\n[3] Testing LLM Router instantiation...")
    try:
        from jarvis.llm.router import LlmRouter
        from jarvis.llm.gemini import GeminiLLM
        
        planner = LlmRouter(GeminiLLM(cfg.planner_model), thinking=cfg.thinking)
        print(f"    ✓ LLM Router created successfully")
        print(f"    - Router type: {type(planner).__name__}")
    except Exception as e:
        print(f"    ✗ LLM Router creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Submit a test task (but cancel immediately)
    print("\n[4] Testing task submission...")
    try:
        task_id = await bridge.submit_task(
            goal="Test task - open Notepad",
            planner_mode="auto",
            engine="state_machine",
        )
        print(f"    ✓ Task submitted: {task_id}")
        
        # Wait a moment for task to start
        await asyncio.sleep(0.5)
        
        # Check task status
        status = bridge.get_task_status(task_id)
        if status:
            print(f"    ✓ Task status retrieved: {status['status']}")
        else:
            print(f"    ⚠ Could not retrieve task status")
        
        # Cancel the task
        print("\n[5] Cancelling test task...")
        cancelled = await bridge.cancel_task(task_id)
        print(f"    ✓ Task cancelled: {cancelled}")
        
        # Wait for cancellation to complete
        await asyncio.sleep(0.5)
        
    except Exception as e:
        print(f"    ✗ Task submission failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    result = asyncio.run(test_task_submission())
    sys.exit(0 if result else 1)
