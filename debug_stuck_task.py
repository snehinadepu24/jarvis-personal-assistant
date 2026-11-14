"""
Debug script to identify where task execution gets stuck
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

async def test_task_execution():
    print("\n" + "="*60)
    print("DEBUGGING TASK EXECUTION")
    print("="*60)
    
    try:
        # Import components
        print("\n1. Importing components...")
        from jarvis.config import Config
        from jarvis.api.bridge import AgentBridge
        print("   ✅ Imports successful")
        
        # Initialize
        print("\n2. Initializing bridge...")
        cfg = Config()
        bridge = AgentBridge.get_instance(cfg)
        print("   ✅ Bridge initialized")
        
        # Submit task
        print("\n3. Submitting task...")
        task_id = await bridge.submit_task(
            goal="open notepad",
            planner_mode="auto"
        )
        print(f"   ✅ Task submitted: {task_id}")
        
        # Monitor execution with timeout
        print("\n4. Monitoring execution (30s timeout)...")
        start_time = asyncio.get_event_loop().time()
        timeout = 30
        
        while True:
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                print(f"\n   ⚠️  TIMEOUT after {elapsed:.1f}s")
                break
            
            # Check status
            task = bridge.tasks.get(task_id)
            if task:
                print(f"   Status: {task.status}, Steps: {task.steps}", end="\r")
                
                if task.status in ["completed", "failed", "cancelled"]:
                    print(f"\n   ✅ Task {task.status}")
                    print(f"   Summary: {task.summary}")
                    if task.error:
                        print(f"   Error: {task.error}")
                    break
            
            await asyncio.sleep(0.5)
        
        # Get final status
        final_task = bridge.tasks.get(task_id)
        if final_task:
            print(f"\n5. Final State:")
            print(f"   Status: {final_task.status}")
            print(f"   Steps: {final_task.steps}")
            print(f"   Summary: {final_task.summary}")
            if final_task.error:
                print(f"   Error: {final_task.error}")
            
            # Check context
            if final_task.ctx:
                print(f"\n6. Context Info:")
                print(f"   LLM: {final_task.ctx.llm}")
                print(f"   Backend: {final_task.ctx.backend}")
                print(f"   Executor: {final_task.ctx.executor}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\nThis will test task execution and identify where it gets stuck.")
    print("If the task hangs, check:")
    print("  - Gemini API key is set")
    print("  - Network connectivity")
    print("  - State machine is running")
    
    asyncio.run(test_task_execution())
