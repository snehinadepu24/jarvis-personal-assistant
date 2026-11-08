from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from jarvis.agent.budgets import Budgets

ROOT = Path(__file__).resolve().parent.parent


def _load_env(paths: list[Path]) -> None:
    for p in paths:
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip().strip('"'), v.strip().strip('"'))


@dataclass
class Config:
    planner_provider: str = "gemini"
    planner_model: str = "gemini-2.5-flash"
    thinking: str = "low"
    intent_mode: str = "heuristic"
    budgets: Budgets = field(default_factory=Budgets)
    data_dir: Path = ROOT / "jarvis_data"
    backend: str = "auto"
    route2_confidence: float = 0.55
    idle_ms: int = 300
    idle_timeout_s: int = 5
    gate_cancel_window_s: float = 2.0
    gate_timeout_s: float = 30.0
    gate_speak: bool = True

    @classmethod
    def load(cls, root: Path | None = None) -> "Config":
        root = root or ROOT
        # Check jarvis/.env, workspace root .env, backend/.env, and current directory .env
        _load_env([
            root / ".env",
            root.parent / ".env",
            root.parent / "backend" / ".env",
            Path.cwd() / ".env"
        ])
        cfg = cls()
        toml_path = root / "jarvis.toml"
        if toml_path.exists():
            data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
            planner = data.get("planner", {})
            cfg.planner_provider = os.environ.get("PLANNER_PROVIDER") or planner.get("provider", cfg.planner_provider)
            cfg.planner_model = os.environ.get("GEMINI_MODEL") or planner.get("model", cfg.planner_model)
            cfg.thinking = os.environ.get("GEMINI_THINKING") or planner.get("thinking", cfg.thinking)
            cfg.intent_mode = data.get("intent", {}).get("mode", cfg.intent_mode)
            b = data.get("budgets", {})
            if b:
                cfg.budgets = Budgets(
                    steps=b.get("steps", 25),
                    llm_calls=b.get("llm_calls", 40),
                    usd=b.get("usd", 0.50),
                    seconds=b.get("seconds", 300),
                    vlm=b.get("vlm", 3),
                )
            paths = data.get("paths", {})
            if paths.get("data_dir"):
                cfg.data_dir = (root / paths["data_dir"]).resolve()
            r = data.get("router", {})
            cfg.route2_confidence = r.get("route2_confidence", cfg.route2_confidence)
            cfg.idle_ms = r.get("idle_ms", cfg.idle_ms)
            cfg.idle_timeout_s = r.get("idle_timeout_s", cfg.idle_timeout_s)
            g = data.get("gate", {})
            cfg.gate_cancel_window_s = g.get("cancel_window_s", cfg.gate_cancel_window_s)
            cfg.gate_timeout_s = g.get("timeout_s", cfg.gate_timeout_s)
            cfg.gate_speak = g.get("speak", cfg.gate_speak)
        else:
            cfg.planner_model = os.environ.get("GEMINI_MODEL", cfg.planner_model)
        cfg.backend = os.environ.get("JARVIS_BACKEND", cfg.backend)
        cfg.data_dir.mkdir(parents=True, exist_ok=True)
        return cfg

    @property
    def audit_db(self) -> Path:
        return self.data_dir / "audit.db"

    @property
    def skills_dir(self) -> Path:
        return self.data_dir / "skills"
