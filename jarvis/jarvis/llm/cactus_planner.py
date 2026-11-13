"""
Cactus Needle Local Planner
100% local AI planning using Cactus Needle (26M parameter model)
Zero API costs, complete privacy, offline capability
"""
from __future__ import annotations

import asyncio
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

try:
    import cactus
    CACTUS_AVAILABLE = True
except ImportError:
    CACTUS_AVAILABLE = False
    cactus = None

from jarvis.core.schema import Step, Click, SetText, Hotkey, Done, Fail, Wait
from jarvis.llm.base import Usage


class CactusPlanner:
    """
    Local AI planner using Cactus Needle.
    Drop-in replacement for GeminiLLM with zero API costs.
    
    Benefits:
    - 100% local inference (no API calls)
    - Zero costs after model download
    - Complete privacy (no data leaves device)
    - Works offline
    - 26M parameter model (distilled from Gemini)
    """
    
    name = "cactus-needle-local"
    
    def __init__(self):
        if not CACTUS_AVAILABLE:
            raise RuntimeError("cactus-compute not installed. Run: pip install -U cactus-compute")
        
        self.model_loaded = False
        self._init_agent()
    
    def _init_agent(self):
        """Initialize Cactus agent with JARVIS action tools"""
        
        @cactus.tool
        def click_element(mark: int, reason: str = "") -> dict:
            """Click a UI element by its mark number"""
            return {"action": "click", "mark": mark, "reason": reason}
        
        @cactus.tool
        def double_click_element(mark: int, reason: str = "") -> dict:
            """Double-click a UI element"""
            return {"action": "double_click", "mark": mark, "reason": reason}
        
        @cactus.tool
        def right_click_element(mark: int, reason: str = "") -> dict:
            """Right-click a UI element"""
            return {"action": "right_click", "mark": mark, "reason": reason}
        
        @cactus.tool
        def type_text(text: str, mark: int = 0, submit: bool = False, reason: str = "") -> dict:
            """Type text into element. mark=0 types into focused window."""
            return {"action": "type", "text": text, "mark": mark, "submit": submit, "reason": reason}
        
        @cactus.tool
        def press_hotkey(keys: str, reason: str = "") -> dict:
            """Press keyboard hotkey (e.g., 'ctrl+c', 'alt+f4')"""
            return {"action": "hotkey", "keys": keys, "reason": reason}
        
        @cactus.tool
        def open_application(name: str, reason: str = "") -> dict:
            """Open or switch to an application"""
            return {"action": "open_app", "name": name, "reason": reason}
        
        @cactus.tool
        def focus_window(title_contains: str, reason: str = "") -> dict:
            """Focus a window by title substring"""
            return {"action": "focus_window", "title_contains": title_contains, "reason": reason}
        
        @cactus.tool
        def wait_seconds(seconds: float, reason: str = "") -> dict:
            """Wait for specified seconds"""
            return {"action": "wait", "seconds": seconds, "reason": reason}
        
        @cactus.tool
        def task_complete(summary: str, reason: str = "") -> dict:
            """Mark task as successfully completed"""
            return {"action": "done", "summary": summary, "reason": reason}
        
        @cactus.tool
        def task_failed(error: str, reason: str = "") -> dict:
            """Mark task as failed"""
            return {"action": "fail", "error": error, "reason": reason}
        
        # Create agent with all tools
        self.agent = cactus.Cactus(tools=[
            click_element,
            double_click_element,
            right_click_element,
            type_text,
            press_hotkey,
            open_application,
            focus_window,
            wait_seconds,
            task_complete,
            task_failed,
        ])
        
        print("[Cactus Planner] Needle agent initialized with JARVIS tools")
    
    async def intent(self, goal: str) -> dict:
        """
        Analyze user intent from goal.
        
        Args:
            goal: User's task goal
        
        Returns:
            Intent dict with categories and complexity
        """
        try:
            prompt = f"""Analyze this task request:
"{goal}"

What is the user trying to accomplish? Categorize as:
- ui_automation: Interacting with desktop applications
- web_browsing: Web-related tasks
- file_management: File/folder operations
- system_control: System settings/control
- information_retrieval: Getting information

Complexity: simple, medium, or complex?

Return: {{"category": str, "complexity": str, "requires_ui": bool}}"""
            
            result = await asyncio.to_thread(self.agent.run, prompt)
            
            if not self.model_loaded:
                self.model_loaded = True
                print("[Cactus Planner] Needle model loaded successfully")
            
            # Parse result
            if result and "results" in result:
                return result["results"]
            
            # Fallback
            return {
                "category": "ui_automation",
                "complexity": "medium",
                "requires_ui": True
            }
        
        except Exception as e:
            print(f"[Cactus Planner] Intent analysis error: {e}")
            return {
                "category": "unknown",
                "complexity": "medium",
                "requires_ui": True,
                "error": str(e)
            }
    
    async def plan(
        self,
        goal: str,
        memory: str,
        step_no: int,
        max_steps: int,
        last_action: str,
        last_result: str,
        screen,
        screen_diff: str,
        window_line: str,
        route: int,
        screenshot=None,
    ) -> Tuple[Step, Usage]:
        """
        Plan next action using Cactus Needle.
        
        Args:
            goal: User's task goal
            memory: Progress memory
            step_no: Current step number
            max_steps: Maximum allowed steps
            last_action: Last action taken
            last_result: Result of last action
            screen: Current screen observation
            screen_diff: Screen changes description
            window_line: Window info line
            route: Observation route used
            screenshot: Optional screenshot bytes
        
        Returns:
            (Step, Usage) tuple
        """
        try:
            # Build context for Needle
            context = self._build_context(
                goal, memory, step_no, max_steps,
                last_action, last_result, screen,
                screen_diff, window_line
            )
            
            # Get plan from Needle
            result = await asyncio.to_thread(self.agent.run, context)
            
            if not self.model_loaded:
                self.model_loaded = True
                print("[Cactus Planner] Needle model loaded successfully")
            
            # Parse result into Step
            step = self._parse_result_to_step(result, screen)
            
            # Usage tracking (local model = zero cost)
            usage = Usage(
                model="cactus-needle-local",
                input_tokens=len(context) // 4,  # Estimate
                output_tokens=50,  # Estimate
                usd=0.0  # Local = free!
            )
            
            return step, usage
        
        except Exception as e:
            print(f"[Cactus Planner] Planning error: {e}")
            
            # Fallback to safe action
            step = Step(
                thought=f"Error in planning: {e}",
                action=Fail(type="fail", error=str(e), reason="planning_error"),
                expect="Task failed"
            )
            
            usage = Usage(model="cactus-needle-local", input_tokens=0, output_tokens=0, usd=0.0)
            return step, usage
    
    def _build_context(
        self,
        goal: str,
        memory: str,
        step_no: int,
        max_steps: int,
        last_action: str,
        last_result: str,
        screen,
        screen_diff: str,
        window_line: str
    ) -> str:
        """Build context prompt for Needle"""
        
        # Build UI element list
        elements = []
        if screen and hasattr(screen, 'elements'):
            for el in screen.elements[:20]:  # Limit to top 20
                role = getattr(el, 'role', 'unknown')
                name = getattr(el, 'name', '')
                mark = getattr(el, 'mark', 0)
                elements.append(f"  [{mark}] {role}: {name}")
        
        elements_str = "\n".join(elements) if elements else "  (no elements detected)"
        
        context = f"""You are JARVIS, a desktop automation assistant.

GOAL: {goal}

CURRENT STATE:
Step {step_no}/{max_steps}
Window: {window_line}
{screen_diff}

UI ELEMENTS:
{elements_str}

PROGRESS:
{memory}

LAST ACTION: {last_action}
RESULT: {last_result}

Plan the NEXT SINGLE ACTION to progress toward the goal.
Use the provided tools (click_element, type_text, press_hotkey, etc.).
Think step-by-step. Be precise with mark numbers.

If goal is achieved, call task_complete().
If stuck or impossible, call task_failed()."""
        
        return context
    
    def _parse_result_to_step(self, result: dict, screen) -> Step:
        """Parse Cactus result into JARVIS Step"""
        
        # Extract tool calls from result
        if not result or "results" not in result:
            return Step(
                thought="No valid plan generated",
                action=Wait(type="wait", seconds=1.0, reason="planning_issue"),
                expect="Wait for clarity"
            )
        
        tool_results = result["results"]
        
        # Parse first tool call
        if isinstance(tool_results, list) and len(tool_results) > 0:
            tool_call = tool_results[0]
        elif isinstance(tool_results, dict):
            tool_call = tool_results
        else:
            tool_call = {}
        
        action_type = tool_call.get("action", "wait")
        
        # Build thought
        thought = tool_call.get("reason", f"Execute {action_type}")
        
        # Parse action
        if action_type == "click":
            action = Click(
                type="click",
                mark=tool_call.get("mark", 0),
                reason=tool_call.get("reason", "")
            )
            expect = f"Element {tool_call.get('mark')} clicked"
        
        elif action_type == "double_click":
            action = Click(
                type="double_click",
                mark=tool_call.get("mark", 0),
                reason=tool_call.get("reason", "")
            )
            expect = f"Element {tool_call.get('mark')} double-clicked"
        
        elif action_type == "right_click":
            action = Click(
                type="right_click",
                mark=tool_call.get("mark", 0),
                reason=tool_call.get("reason", "")
            )
            expect = f"Element {tool_call.get('mark')} right-clicked"
        
        elif action_type == "type":
            action = SetText(
                type="type",
                text=tool_call.get("text", ""),
                mark=tool_call.get("mark", 0),
                submit=tool_call.get("submit", False),
                reason=tool_call.get("reason", "")
            )
            expect = f"Typed: {tool_call.get('text', '')[:30]}"
        
        elif action_type == "hotkey":
            action = Hotkey(
                type="hotkey",
                keys=tool_call.get("keys", ""),
                reason=tool_call.get("reason", "")
            )
            expect = f"Pressed {tool_call.get('keys')}"
        
        elif action_type == "done":
            action = Done(
                type="done",
                summary=tool_call.get("summary", "Task completed"),
                reason=tool_call.get("reason", "")
            )
            expect = "Task complete"
        
        elif action_type == "fail":
            action = Fail(
                type="fail",
                error=tool_call.get("error", "Task failed"),
                reason=tool_call.get("reason", "")
            )
            expect = "Task failed"
        
        else:
            # Default wait
            action = Wait(
                type="wait",
                seconds=tool_call.get("seconds", 1.0),
                reason=tool_call.get("reason", "")
            )
            expect = "Wait briefly"
        
        return Step(thought=thought, action=action, expect=expect)
    
    def get_model_info(self) -> Dict[str, any]:
        """Get model information"""
        return {
            "name": "Cactus Needle",
            "parameters": "26M",
            "size_mb": 26,
            "distilled_from": "Gemini",
            "features": ["tool_calling", "structured_extraction"],
            "local": True,
            "cost_per_task": 0.0,
            "privacy": "complete"
        }


def create_cactus_planner() -> CactusPlanner:
    """Create Cactus Needle planner instance"""
    return CactusPlanner()
