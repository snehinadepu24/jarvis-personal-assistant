"""
Cactus Mirage Vision Backend
Local vision model for UI understanding and element detection
"""
from __future__ import annotations

import asyncio
from typing import List, Dict, Optional
from pathlib import Path
import tempfile

try:
    import cactus
    CACTUS_AVAILABLE = True
except ImportError:
    CACTUS_AVAILABLE = False
    cactus = None

from jarvis.core.schema import Screen, UiElement, Rect


class CactusVisionBackend:
    """
    Vision-based UI observation using Cactus Mirage.
    
    Features:
    - Local image understanding
    - Extract UI elements from screenshots
    - Describe visual content
    - No cloud API needed
    """
    
    def __init__(self):
        if not CACTUS_AVAILABLE:
            raise RuntimeError("cactus-compute not installed. Run: pip install -U cactus-compute")
        
        self.mirage = cactus.Mirage()
        self.model_loaded = False
        print("[Cactus Vision] Mirage model initializing...")
    
    async def observe_visual(self, screenshot_path: str, app: str = "", window_title: str = "") -> Screen:
        """
        Observe screen using vision model.
        
        Args:
            screenshot_path: Path to screenshot image
            app: Application name (optional)
            window_title: Window title (optional)
        
        Returns:
            Screen with vision-detected elements
        """
        try:
            # Get visual description
            description = await asyncio.to_thread(
                self.mirage.describe,
                screenshot_path
            )
            
            if not self.model_loaded:
                self.model_loaded = True
                print("[Cactus Vision] Mirage model loaded successfully")
            
            # Extract UI elements
            elements = await self._extract_ui_elements(screenshot_path)
            
            return Screen(
                app=app or "vision-detected",
                window_title=window_title or description[:50],
                elements=elements,
                hwnd=0,  # Vision doesn't have HWND
                metadata={
                    "description": description,
                    "method": "cactus_mirage",
                    "element_count": len(elements)
                }
            )
        
        except Exception as e:
            print(f"[Cactus Vision] Observation error: {e}")
            return Screen(
                app=app or "error",
                window_title=window_title or "Vision failed",
                elements=[],
                hwnd=0,
                metadata={"error": str(e), "method": "cactus_mirage"}
            )
    
    async def _extract_ui_elements(self, screenshot_path: str) -> List[UiElement]:
        """Extract UI elements from screenshot using Mirage"""
        try:
            # Define extraction schema
            schema = {
                "ui_elements": [
                    {
                        "role": "str",  # button, textbox, label, etc.
                        "name": "str",  # Element text/label
                        "position": "str",  # top-left, center, etc.
                        "confidence": "float"
                    }
                ]
            }
            
            # Extract with Mirage
            result = await asyncio.to_thread(
                self.mirage.extract,
                schema,
                screenshot_path
            )
            
            # Parse into UiElement objects
            elements = []
            if result and "ui_elements" in result:
                for i, elem_data in enumerate(result["ui_elements"][:50]):  # Limit to 50
                    elements.append(UiElement(
                        mark=i + 1,
                        role=elem_data.get("role", "unknown"),
                        name=elem_data.get("name", ""),
                        control_type=self._role_to_control_type(elem_data.get("role", "")),
                        rect=self._position_to_rect(elem_data.get("position", "center")),
                        enabled=True,
                        key=f"vision_{i}",
                        metadata={
                            "confidence": elem_data.get("confidence", 0.5),
                            "method": "cactus_mirage"
                        }
                    ))
            
            return elements
        
        except Exception as e:
            print(f"[Cactus Vision] Element extraction error: {e}")
            return []
    
    def _role_to_control_type(self, role: str) -> int:
        """Map role string to UIA control type"""
        role_map = {
            "button": 50000,
            "textbox": 50004,
            "label": 50020,
            "link": 50005,
            "image": 50008,
            "checkbox": 50002,
            "radio": 50003,
            "menu": 50009,
            "menuitem": 50011,
            "list": 50008,
            "listitem": 50007,
            "tree": 50023,
            "treeitem": 50024,
            "tab": 50018,
            "window": 50032,
            "pane": 50033,
        }
        return role_map.get(role.lower(), 50033)  # Default to pane
    
    def _position_to_rect(self, position: str) -> Rect:
        """Convert position description to approximate Rect"""
        # Parse position like "top-left", "center", "bottom-right"
        # This is approximate - vision doesn't give exact coordinates
        
        position_map = {
            "top-left": (50, 50, 250, 100),
            "top-center": (400, 50, 600, 100),
            "top-right": (750, 50, 950, 100),
            "center-left": (50, 300, 250, 350),
            "center": (400, 300, 600, 350),
            "center-right": (750, 300, 950, 350),
            "bottom-left": (50, 550, 250, 600),
            "bottom-center": (400, 550, 600, 600),
            "bottom-right": (750, 550, 950, 600),
        }
        
        coords = position_map.get(position.lower(), (400, 300, 600, 350))
        return Rect(l=coords[0], t=coords[1], r=coords[2], b=coords[3])
    
    async def describe_scene(self, screenshot_path: str) -> str:
        """Get natural language description of screenshot"""
        try:
            description = await asyncio.to_thread(
                self.mirage.describe,
                screenshot_path
            )
            return description
        except Exception as e:
            print(f"[Cactus Vision] Scene description error: {e}")
            return ""
    
    async def validate_action_visually(
        self,
        before_path: str,
        after_path: str,
        expected_change: str
    ) -> bool:
        """
        Validate that an action had expected visual effect.
        
        Args:
            before_path: Screenshot before action
            after_path: Screenshot after action
            expected_change: What should have changed (e.g., "button became highlighted")
        
        Returns:
            True if change matches expectation
        """
        try:
            # Describe both screenshots
            before_desc = await self.describe_scene(before_path)
            after_desc = await self.describe_scene(after_path)
            
            # Simple heuristic: check if descriptions are meaningfully different
            # and if expected_change keywords appear in after_desc
            
            if expected_change:
                keywords = expected_change.lower().split()
                after_lower = after_desc.lower()
                
                matches = sum(1 for kw in keywords if kw in after_lower)
                return matches >= len(keywords) / 2
            
            # If no specific expectation, just check for any change
            return before_desc != after_desc
        
        except Exception as e:
            print(f"[Cactus Vision] Visual validation error: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, any]:
        """Get model information"""
        return {
            "name": "Cactus Mirage",
            "type": "vision",
            "features": ["image_description", "structured_extraction", "UI_understanding"],
            "local": True,
            "privacy": "complete"
        }


# Singleton instance
_backend = None

def get_vision_backend() -> CactusVisionBackend:
    """Get singleton vision backend instance"""
    global _backend
    if _backend is None:
        _backend = CactusVisionBackend()
    return _backend


async def observe_with_vision(screenshot_path: str, app: str = "", window_title: str = "") -> Screen:
    """Convenience function to observe using vision"""
    backend = get_vision_backend()
    return await backend.observe_visual(screenshot_path, app, window_title)
