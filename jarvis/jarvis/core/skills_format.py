from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SkillStep(BaseModel):
    select: dict = Field(default_factory=dict)
    action: dict
    postcondition: str = ""


class SkillModel(BaseModel):
    name: str
    version: int = 1
    triggers: list[str] = []
    params: dict[str, str] = {}
    steps: list[SkillStep]

    @classmethod
    def load(cls, path: Path) -> "SkillModel":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(self.model_dump(), sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )


def match_selector(elem, select: dict) -> bool:
    if not select:
        return False
    if select.get("automation_id") and elem.automation_id != select["automation_id"]:
        return False
    if select.get("name_exact") and elem.name != select["name_exact"]:
        return False
    if select.get("name") and select["name"].lower() not in elem.name.lower():
        return False
    if select.get("role") and elem.role != select["role"]:
        return False
    if select.get("control_type") is not None and elem.control_type != select["control_type"]:
        return False
    if select.get("patterns"):
        if not set(select["patterns"]).issubset(set(elem.patterns)):
            return False
    return bool(select.get("automation_id") or select.get("name") or select.get("name_exact") or select.get("role") or select.get("control_type") is not None)


def resolve_element(screen, select: dict):
    chain = select if isinstance(select, list) else [select]
    for step_sel in chain:
        if not step_sel:
            continue
        found = [e for e in screen.elements if match_selector(e, step_sel)]
        if found:
            return found[0]
    return None
