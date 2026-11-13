"""
Common scripted task patterns for faster, more reliable execution.
"""
from jarvis.agent.skills import ScriptEntry, ScriptedPlanner

def open_notepad_and_type(text: str) -> ScriptedPlanner:
    """Fast scripted version of opening Notepad and typing.
    Uses direct app launch for maximum speed and reliability."""
    return ScriptedPlanner([
        ScriptEntry(
            thought="Launch Notepad directly",
            action={"type": "open_app", "name": "Notepad", "reason": "fastest launch method"},
            expect="Notepad opening"
        ),
        ScriptEntry(
            thought="Wait for Notepad window to be ready",
            action={"type": "wait", "seconds": 1.0, "reason": "ensure window loaded"},
            expect="Notepad ready"
        ),
        ScriptEntry(
            thought=f"Type the message: {text}",
            action={"type": "type", "text": text, "reason": "write message", "submit": False},
            expect="text written"
        ),
        ScriptEntry(
            thought="Task completed successfully",
            action={"type": "done", "summary": f"Opened Notepad and wrote: {text}", "reason": "complete"},
            expect="-"
        ),
    ])

def open_app_fast(app_name: str) -> ScriptedPlanner:
    """Fast app launch using Win+R."""
    return ScriptedPlanner([
        ScriptEntry(
            thought=f"Launch {app_name} via Run dialog",
            action={"type": "hotkey", "keys": "win+r", "reason": "open run"},
            expect="Run dialog open"
        ),
        ScriptEntry(
            thought="Wait for dialog",
            action={"type": "wait", "seconds": 0.5, "reason": "dialog ready"},
            expect="ready"
        ),
        ScriptEntry(
            thought=f"Type {app_name}",
            action={"type": "type", "text": app_name.lower(), "reason": "app name", "submit": False},
            expect="command typed"
        ),
        ScriptEntry(
            thought="Execute",
            action={"type": "hotkey", "keys": "enter", "reason": "launch"},
            expect=f"{app_name} launching"
        ),
        ScriptEntry(
            thought="Wait for app",
            action={"type": "wait", "seconds": 1.5, "reason": "load time"},
            expect="app ready"
        ),
        ScriptEntry(
            thought="Done",
            action={"type": "done", "summary": f"Launched {app_name}", "reason": "complete"},
            expect="-"
        ),
    ])

# Common app commands for Win+R
QUICK_LAUNCH = {
    "notepad": "notepad",
    "calculator": "calc",
    "settings": "ms-settings:",
    "task manager": "taskmgr",
    "command prompt": "cmd",
    "powershell": "powershell",
    "file explorer": "explorer",
    "control panel": "control",
    "paint": "mspaint",
    "snipping tool": "snippingtool",
}

def get_script_for_goal(goal: str) -> ScriptedPlanner | None:
    """Match goal to a pre-defined script for faster execution."""
    goal_lower = goal.lower()
    
    # Pattern: "open notepad and write/type X"
    if "notepad" in goal_lower and ("write" in goal_lower or "type" in goal_lower):
        # Extract text to type
        for keyword in ["write", "type"]:
            if keyword in goal_lower:
                text = goal_lower.split(keyword)[-1].strip().rstrip('.')
                return open_notepad_and_type(text)
    
    # Pattern: "open/launch [app]"
    for trigger in ["open", "launch", "start"]:
        if trigger in goal_lower:
            for app_name, command in QUICK_LAUNCH.items():
                if app_name in goal_lower:
                    return open_app_fast(app_name)
    
    return None
