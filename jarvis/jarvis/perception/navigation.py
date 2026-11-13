"""
Complex UI Navigation - Phase 4 Enhancement
Handles multi-level menus, nested dialogs, and difficult navigation
"""
from __future__ import annotations

from typing import List, Optional, Tuple
from dataclasses import dataclass
import asyncio

@dataclass
class NavigationStep:
    """A single step in complex navigation"""
    action_type: str  # click, hover, type, wait
    target: str  # Element description
    mark: Optional[int] = None
    text: Optional[str] = None
    wait_after: float = 0.3


class NavigationStrategy:
    """
    Handles complex multi-level UI navigation.
    
    Strategies:
    1. Breadcrumb tracking - remember path through menus
    2. Hover-then-click - for cascading menus
    3. Wait-and-retry - for dynamic UIs
    4. VLM fallback - for custom controls
    """
    
    def __init__(self, backend, executor):
        self.backend = backend
        self.executor = executor
        self.breadcrumbs: List[NavigationStep] = []
        self.max_depth = 5
    
    async def navigate_menu_path(
        self, 
        path: List[str],
        start_hotkey: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Navigate through multi-level menu.
        
        Args:
            path: List of menu item names to click in order
                  e.g., ["File", "Open", "Recent Files"]
            start_hotkey: Optional hotkey to open first menu (e.g., "alt+f")
            
        Returns:
            (success, detail_message)
        """
        self.breadcrumbs.clear()
        
        # Open menu if hotkey provided
        if start_hotkey:
            from jarvis.core.schema import Hotkey, Step
            action = Hotkey(type="hotkey", keys=start_hotkey, reason="open menu")
            step = Step(thought="Open menu", action=action, expect="Menu visible")
            result = await self.executor.apply(step)
            
            if not result.ok:
                return False, f"Failed to open menu: {result.detail}"
            
            await asyncio.sleep(0.3)
        
        # Navigate each level
        for depth, menu_item in enumerate(path):
            if depth >= self.max_depth:
                return False, f"Max depth {self.max_depth} exceeded"
            
            success, detail = await self._navigate_to_item(menu_item, depth)
            
            if not success:
                # Try recovery
                success, detail = await self._recover_navigation(menu_item, depth)
                
                if not success:
                    return False, detail
            
            # Record breadcrumb
            self.breadcrumbs.append(NavigationStep(
                action_type="click",
                target=menu_item,
                wait_after=0.3
            ))
        
        return True, f"Navigated through {len(path)} levels"
    
    async def _navigate_to_item(
        self, 
        target_name: str, 
        depth: int
    ) -> Tuple[bool, str]:
        """Navigate to a specific menu item at given depth"""
        from jarvis.core.schema import Click, Step
        
        # Observe current screen
        screen = await self.backend.observe(route=2)
        
        # Find target element
        target_el = None
        for el in screen.elements:
            name = getattr(el, 'name', '') or getattr(el, 'label', '')
            if target_name.lower() in name.lower():
                role = getattr(el, 'role', '')
                if role in ['menuitem', 'button', 'tab', 'link']:
                    target_el = el
                    break
        
        if target_el is None:
            return False, f"Menu item '{target_name}' not found"
        
        # Click the element
        action = Click(type="click", mark=target_el.mark, reason=f"select {target_name}")
        step = Step(thought=f"Click {target_name}", action=action, expect="Item selected")
        result = await self.executor.apply(step, screen)
        
        if result.ok:
            await asyncio.sleep(0.3)  # Wait for submenu/dialog
            return True, f"Clicked {target_name}"
        
        return False, result.detail
    
    async def _recover_navigation(
        self, 
        target_name: str, 
        depth: int
    ) -> Tuple[bool, str]:
        """
        Attempt recovery when navigation fails.
        
        Recovery strategies:
        1. Refresh observation
        2. Try hover-then-click
        3. Use keyboard navigation
        4. Fall back to VLM
        """
        # Strategy 1: Wait and refresh
        await asyncio.sleep(0.5)
        screen = await self.backend.observe(route=2)
        
        # Try again with fresh observation
        success, detail = await self._navigate_to_item(target_name, depth)
        if success:
            return True, detail
        
        # Strategy 2: Try keyboard navigation
        # Many menus support arrow keys and enter
        from jarvis.core.schema import Hotkey, Step
        
        # Press down arrow to move selection
        down_action = Hotkey(type="hotkey", keys="down", reason="navigate")
        await self.executor.apply(Step(thought="Move down", action=down_action, expect=""), screen)
        
        # Try enter
        enter_action = Hotkey(type="hotkey", keys="enter", reason="select")
        result = await self.executor.apply(Step(thought="Select", action=enter_action, expect=""), screen)
        
        if result.ok:
            return True, "Selected via keyboard"
        
        # Strategy 3: VLM fallback
        if self.backend and hasattr(self.backend, 'observe'):
            vlm_screen = await self.backend.observe(route=4)  # VLM route
            # Would use VLM to find and click element
            # For now, report failure
        
        return False, f"All recovery strategies failed for '{target_name}'"
    
    async def navigate_dialog_sequence(
        self, 
        steps: List[dict]
    ) -> Tuple[bool, str]:
        """
        Navigate through a sequence of dialogs.
        
        Args:
            steps: List of dialog interaction steps
                   e.g., [
                       {"type": "click", "target": "Browse"},
                       {"type": "type", "text": "C:\\path"},
                       {"type": "click", "target": "OK"}
                   ]
                   
        Returns:
            (success, detail)
        """
        for i, step_spec in enumerate(steps):
            screen = await self.backend.observe(route=2)
            
            step_type = step_spec.get("type")
            
            if step_type == "click":
                success, detail = await self._click_dialog_button(
                    step_spec.get("target"), 
                    screen
                )
            elif step_type == "type":
                success, detail = await self._type_in_dialog(
                    step_spec.get("text"), 
                    screen
                )
            elif step_type == "wait":
                await asyncio.sleep(step_spec.get("seconds", 0.5))
                success, detail = True, "Waited"
            else:
                success, detail = False, f"Unknown step type: {step_type}"
            
            if not success:
                return False, f"Step {i+1} failed: {detail}"
            
            await asyncio.sleep(0.3)
        
        return True, f"Completed {len(steps)} dialog steps"
    
    async def _click_dialog_button(
        self, 
        button_name: str, 
        screen
    ) -> Tuple[bool, str]:
        """Click a button in a dialog"""
        from jarvis.core.schema import Click, Step
        
        # Find button
        button_el = None
        for el in screen.elements:
            name = getattr(el, 'name', '')
            if button_name.lower() in name.lower():
                role = getattr(el, 'role', '')
                if role in ['button', 'pushbutton']:
                    button_el = el
                    break
        
        if button_el is None:
            return False, f"Button '{button_name}' not found"
        
        action = Click(type="click", mark=button_el.mark, reason=f"click {button_name}")
        step = Step(thought=f"Click {button_name}", action=action, expect="Button clicked")
        result = await self.executor.apply(step, screen)
        
        return result.ok, result.detail
    
    async def _type_in_dialog(
        self, 
        text: str, 
        screen
    ) -> Tuple[bool, str]:
        """Type text in dialog (usually into focused field)"""
        from jarvis.core.schema import SetText, Step
        
        # Use focused-window typing (mark=0)
        action = SetText(type="type", text=text, mark=0, reason="enter text", submit=False)
        step = Step(thought="Enter text", action=action, expect="Text entered")
        result = await self.executor.apply(step, screen)
        
        return result.ok, result.detail


def create_navigation_strategy(backend, executor) -> NavigationStrategy:
    """Create navigation strategy instance"""
    return NavigationStrategy(backend, executor)
