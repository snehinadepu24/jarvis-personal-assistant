from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any


class ProceduralMemory:
    """Tier 5: Procedural knowledge, recorded skills, keyboard shortcuts, and macro playbooks."""

    def __init__(self, skills_dir: Path | str | None = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path("./jarvis_data/skills")
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._shortcuts: dict[str, str] = {
            "save": "ctrl+s",
            "copy": "ctrl+c",
            "paste": "ctrl+v",
            "undo": "ctrl+z",
            "redo": "ctrl+y",
            "find": "ctrl+f",
            "select_all": "ctrl+a",
            "new_tab": "ctrl+t",
            "close_tab": "ctrl+w",
            "switch_app": "alt+tab",
            "open_settings": "win+i",
            "open_file_explorer": "win+e",
            "open_run": "win+r",
            "lock_screen": "win+l",
        }

    def get_shortcut(self, action_name: str) -> str | None:
        return self._shortcuts.get(action_name.lower())

    def list_skills(self) -> list[str]:
        return [f.stem for f in self.skills_dir.glob("*.yaml")]

    def load_skill(self, name: str) -> dict | None:
        skill_file = self.skills_dir / f"{name}.yaml"
        if skill_file.exists():
            try:
                return yaml.safe_load(skill_file.read_text(encoding="utf-8"))
            except Exception:
                return None
        return None

    def save_skill(self, name: str, skill_data: dict) -> Path:
        skill_file = self.skills_dir / f"{name}.yaml"
        skill_file.write_text(yaml.safe_dump(skill_data, sort_keys=False), encoding="utf-8")
        return skill_file

