from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class FilesConnector:
    root: Path

    def tiers(self, tool: str) -> int:
        return {"files.read": 0, "files.list": 0, "files.rename": 2, "files.write": 3, "files.delete": 3}.get(tool, 3)

    def handle(self, tool: str, args: dict):
        if tool == "files.read":
            p = self.root / args["name"]
            return _res(p.exists(), p.read_text(encoding="utf-8")[:4000] if p.exists() else "missing", {"path": str(p)})
        if tool == "files.list":
            return _res(True, ", ".join(sorted(p.name for p in self.root.iterdir())) or "(empty)")
        if tool == "files.rename":
            src, dst = self.root / args["name"], self.root / args["to"]
            if not src.exists():
                return _res(False, f"{src} missing")
            src.rename(dst)
            return _res(True, f"renamed to {dst.name}", {"path": str(dst)})
        if tool == "files.write":
            p = self.root / args["name"]
            p.write_text(args.get("content", ""), encoding="utf-8")
            return _res(True, f"wrote {p.name}", {"path": str(p)})
        if tool == "files.delete":
            p = self.root / args["name"]
            if not p.exists():
                return _res(False, f"{p} missing")
            trash = self.root / ".jarvis_trash"
            trash.mkdir(exist_ok=True)
            p.rename(trash / p.name)  # recycle, never hard-delete
            return _res(True, f"moved {p.name} to recycle bin")
        return _res(False, f"unknown files tool {tool}")


def _res(ok: bool, detail: str, artifact: dict | None = None):
    from jarvis.actions.base import ActionResult

    return ActionResult(ok, detail, artifact or {})
