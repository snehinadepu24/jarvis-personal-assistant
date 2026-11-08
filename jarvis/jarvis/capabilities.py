from __future__ import annotations

import json
import sys
from pathlib import Path


def get_system_capabilities() -> dict:
    is_win = sys.platform == "win32"
    has_pywin32 = False
    if is_win:
        try:
            import win32gui
            has_pywin32 = True
        except ImportError:
            pass

    return {
        "version": "2.0.0",
        "platform": {
            "os": sys.platform,
            "is_windows_native": is_win,
            "python_version": sys.version.split()[0],
            "pywin32_available": has_pywin32,
        },
        "perception": {
            "available_routes": [
                {"route": 1, "name": "connector", "description": "Direct application / API connector"},
                {"route": 2, "name": "uia", "description": "Windows UI Automation accessibility tree with snapshot refs"},
                {"route": 3, "name": "ocr_detector", "description": "Tesseract OCR and UI element detection"},
                {"route": 4, "name": "vlm", "description": "Visual Language Model screen screenshot inspection"},
            ],
            "default_route": 2,
            "two_stage_observation": True,
            "snapshot_scoped_references": True,
        },
        "execution": {
            "default_mode": "headless_semantic",
            "semantic_patterns": ["Invoke", "Toggle", "ValuePattern", "SelectionItem", "ExpandCollapse"],
            "physical_input_fallback": is_win,
            "input_mode_auditing": True,
        },
        "connectors": {
            "windows_manager": True,
            "safe_clipboard": True,
            "system_surfaces": True,
            "files": True,
            "mcp_client": True,
            "browser_cdp": True,
            "office_com": is_win,
            "spotify": True,
        },
        "memory_architecture": {
            "tiers": [
                {"tier": 1, "name": "working", "description": "In-flight scratchpad, diffs, and target refs"},
                {"tier": 2, "name": "session", "description": "Short-term thread history and goal stack"},
                {"tier": 3, "name": "episodic", "description": "SQLite + FTS5 full-text task trajectory store"},
                {"tier": 4, "name": "user_consistent", "description": "Long-term persistent user facts, preferences, and quirks"},
                {"tier": 5, "name": "procedural", "description": "Executable skills and shortcut playbooks"},
            ],
            "status": "ready",
        },
        "orchestration": {
            "engines": ["state_machine", "langgraph"],
            "langgraph_checkpointing": {
                "backend": "sqlite",
                "hitl_interruption": True,
                "time_travel_rewind": True,
            },
            "multi_agent_system": {
                "supervisor": True,
                "desktop_specialist": True,
                "safety_reviewer": True,
                "memory_specialist": True,
                "voice_interaction": True,
            },
        },
        "safety": {
            "risk_tiers": [0, 1, 2, 3, 4],
            "nonce_confirmation_required": [3, 4],
            "redaction_active": True,
            "audit_logging": True,
        },
    }


def format_capabilities(as_json: bool = False) -> str:
    caps = get_system_capabilities()
    if as_json:
        return json.dumps(caps, indent=2)

    lines = [
        "=" * 60,
        "JARVIS System & Desktop Capabilities",
        "=" * 60,
        f"Platform: {caps['platform']['os']} (Windows native: {caps['platform']['is_windows_native']})",
        f"Perception Routes: {', '.join(r['name'] for r in caps['perception']['available_routes'])}",
        f"Execution: Default = {caps['execution']['default_mode']} (Semantic: Yes, Physical: {caps['execution']['physical_input_fallback']})",
        f"Memory Tiers: {', '.join(t['name'] for t in caps['memory_architecture']['tiers'])}",
        f"Orchestration Engines: {', '.join(caps['orchestration']['engines'])}",
        f"Checkpointer: {caps['orchestration']['langgraph_checkpointing']['backend']} (HITL: Yes, Rewind: Yes)",
        "=" * 60,
    ]
    return "\n".join(lines)

