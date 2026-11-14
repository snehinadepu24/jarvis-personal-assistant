"""
Background execution mode - allows JARVIS to work without interrupting user
"""
from __future__ import annotations

import asyncio
from typing import Optional, Callable
from dataclasses import dataclass

@dataclass
class BackgroundConfig:
    """Configuration for background execution"""
    enabled: bool = False
    
    # Window management
    restore_focus: bool = True  # Restore user's window after task
    minimize_spawned: bool = True  # Minimize windows JARVIS opens
    use_virtual_desktop: bool = False  # Use separate virtual desktop (Windows 10+)
    
    # Execution timing
    defer_on_user_active: bool = True  # Pause if user is typing/clicking
    idle_threshold_seconds: float = 2.0  # Wait for user idle
    
    # Safety
    require_approval_in_bg: bool = True  # Always ask for Tier 3+ in background
    notify_on_start: bool = True  # Show notification when task starts
    notify_on_complete: bool = True  # Show notification when done


class BackgroundExecutor:
    """
    Executes tasks in background without disrupting user's work.
    
    Strategy:
    1. Detect user activity (keyboard/mouse)
    2. Wait for idle period
    3. Save current window focus
    4. Execute task
    5. Restore focus
    6. Minimize any windows opened
    """
    
    def __init__(self, config: BackgroundConfig):
        self.config = config
        self.user_active = False
        self.saved_window = None
        self._activity_monitor = None
    
    async def execute_in_background(self, task_fn: Callable, *args, **kwargs):
        """
        Execute a task function in background mode.
        
        Args:
            task_fn: Async function to execute
            *args, **kwargs: Arguments to pass to task_fn
            
        Returns:
            Task result
        """
        if not self.config.enabled:
            # Normal execution
            return await task_fn(*args, **kwargs)
        
        # 1. Wait for user to be idle
        if self.config.defer_on_user_active:
            await self._wait_for_idle()
        
        # 2. Save current focus
        if self.config.restore_focus:
            self.saved_window = await self._get_foreground_window()
        
        # 3. Notify user
        if self.config.notify_on_start:
            await self._show_notification("JARVIS task starting in background...")
        
        # 4. Execute task
        try:
            result = await task_fn(*args, **kwargs)
        finally:
            # 5. Restore focus
            if self.config.restore_focus and self.saved_window:
                await self._restore_window(self.saved_window)
            
            # 6. Notify completion
            if self.config.notify_on_complete:
                await self._show_notification("JARVIS task completed")
        
        return result
    
    async def _wait_for_idle(self):
        """Wait for user to stop typing/clicking"""
        import time
        
        last_activity = time.time()
        
        while True:
            # Check if user is active (placeholder - would use actual activity detection)
            is_active = await self._check_user_activity()
            
            if is_active:
                last_activity = time.time()
            
            # If idle long enough, proceed
            idle_time = time.time() - last_activity
            if idle_time >= self.config.idle_threshold_seconds:
                break
            
            await asyncio.sleep(0.5)
    
    async def _check_user_activity(self) -> bool:
        """
        Check if user is currently active.
        
        Would monitor:
        - Keyboard input
        - Mouse movement
        - Window switching
        
        Returns:
            True if user is active
        """
        # Placeholder implementation
        # Real implementation would use:
        # - pynput for keyboard/mouse monitoring
        # - GetLastInputInfo for Windows idle time
        return False
    
    async def _get_foreground_window(self) -> Optional[dict]:
        """Get currently focused window"""
        try:
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return {'hwnd': hwnd, 'title': title}
        except Exception:
            return None
    
    async def _restore_window(self, window: dict):
        """Restore focus to saved window"""
        try:
            import win32gui
            win32gui.SetForegroundWindow(window['hwnd'])
        except Exception as e:
            print(f"[Background] Could not restore window: {e}")
    
    async def _show_notification(self, message: str):
        """Show Windows notification"""
        # Would use Windows Toast notifications
        # For now, just log
        print(f"[Background] {message}")


def create_background_executor(config: Optional[BackgroundConfig] = None) -> BackgroundExecutor:
    """Create background executor instance"""
    if config is None:
        config = BackgroundConfig()
    return BackgroundExecutor(config)
