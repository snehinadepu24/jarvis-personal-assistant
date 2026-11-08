from __future__ import annotations

import inspect
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from jarvis.actions.mock_executor import MockExecutor
from jarvis.agent.state_machine import AgentContext, run_task
from jarvis.connectors.files import FilesConnector
from jarvis.core.schema import Screen
from jarvis.perception.mock_backend import SimulatedDesktop
from jarvis.safety.audit import Audit
from jarvis.safety.gate import ConfirmationGate, auto_approve_confirmer


def _use_mock(cfg) -> bool:
    return cfg.backend == "mock" or (cfg.backend in ("auto", "") and sys.platform != "win32")


@dataclass
class TaskSpec:
    name: str
    goal: str
    max_steps: int = 25
    check: list[dict] = field(default_factory=list)
    script: list[dict] = field(default_factory=list)
    ask_reply: str = "yes"
    setup: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "TaskSpec":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls(
            name=data["name"], goal=data["goal"], max_steps=data.get("max_steps", 25),
            check=data.get("check", []), script=data.get("script", []),
            ask_reply=data.get("ask_reply", "yes"), setup=data.get("setup", {}),
        )


def _scripted_planner(spec: TaskSpec):
    from jarvis.agent.skills import ScriptEntry, ScriptedPlanner

    return ScriptedPlanner([
        ScriptEntry(thought=e["thought"], action=e["action"], expect=e.get("expect", ""), select=e.get("select", {}))
        for e in spec.script
    ])


def build_planner(spec: TaskSpec, mode: str, cfg, skill_path: Path | None = None):
    if mode == "scripted":
        return _scripted_planner(spec)
    if mode == "skill":
        from jarvis.agent.skills import planner_from_skill
        from jarvis.core.skills_format import SkillModel

        return planner_from_skill(SkillModel.load(skill_path))
    if mode == "gemini":
        from jarvis.llm.gemini import GeminiLLM
        from jarvis.llm.router import LlmRouter

        router = LlmRouter(GeminiLLM(cfg.planner_model), thinking=cfg.thinking)
        router.set_goal(spec.goal)
        return router
    raise ValueError(f"unknown planner mode {mode}")


def _observe(backend, route: int = 2):
    obs = backend.observe(route)
    return obs if inspect.isawaitable(obs) else obs


async def run_spec(
    spec: TaskSpec,
    cfg,
    planner_mode: str = "scripted",
    arm: str = "A",
    seed: int = 0,
    approve: str = "auto",
    record_skill_name: str | None = None,
    skill_path: Path | None = None,
    engine: str = "state_machine",
) -> dict:
    fs_root = cfg.data_dir / f"mockfs_{spec.name}_{seed}"
    mock = _use_mock(cfg)
    if mock:
        desktop = SimulatedDesktop(fs_root=fs_root)
        if spec.setup.get("injection_page"):
            desktop.seed_injection_page()
        backend = desktop
        from jarvis.actions.mock_executor import MockExecutor as _ME

        executor = _ME(desktop, FilesConnector(fs_root))
    else:
        from jarvis.perception.base import build_backend

        desktop = None
        backend = build_backend(cfg)
        from jarvis.actions.uia_executor import UiaExecutor

        executor = UiaExecutor(backend, FilesConnector(fs_root))

    audit = Audit(cfg.audit_db.with_name(f"{cfg.audit_db.stem}_{spec.name}_{arm}_{seed}.db"))
    if approve == "console":
        confirmer = None
    elif approve == "deny":
        from jarvis.safety.gate import always_deny_confirmer

        confirmer = always_deny_confirmer
    else:
        confirmer = auto_approve_confirmer
    gate = ConfirmationGate(
        confirmer=confirmer,
        cancel_window_s=cfg.gate_cancel_window_s,
        timeout_s=cfg.gate_timeout_s,
        speak_summary=cfg.gate_speak,
    )
    planner = build_planner(spec, "skill" if skill_path else planner_mode, cfg, skill_path)
    ask_reply = spec.ask_reply

    async def voice_ask(question: str) -> str:
        return ask_reply

    ctx = AgentContext(
        llm=planner,
        backend=backend,
        executor=executor,
        gate=gate,
        audit=audit,
        budgets=cfg.budgets,
        task_name=spec.name,
        voice_ask=voice_ask,
        allow_connectors=(arm in ("A", "D")),
        allow_vlm=False,
        tools_description="(files.* connectors registered)" if arm in ("A", "D") else "(none)",
    )
    t0 = time.monotonic()
    if engine == "langgraph":
        from jarvis.agent.graph.checkpointer import SqliteCheckpointer
        from jarvis.agent.graph.engine import GraphEngine
        from jarvis.memory.manager import MemoryManager

        chk_path = cfg.data_dir / f"checkpoints_{spec.name}_{seed}.db"
        checkpointer = SqliteCheckpointer(chk_path)
        mem = MemoryManager(cfg.data_dir, thread_id=f"{spec.name}_{seed}")
        g_engine = GraphEngine(ctx, checkpointer, memory_manager=mem)
        g_state = await g_engine.run(spec.goal, thread_id=f"thread_{spec.name}_{seed}")
        status = g_state.get("status", "failed")
        summary = g_state.get("summary", "")
        err = g_state.get("error", "")
        m = {
            "steps": g_state.get("step_no", 0),
            "llm_calls": 0,
            "tokens": 0,
            "usd": 0.0,
            "elapsed_s": round(time.monotonic() - t0, 3),
        }
    else:
        outcome = await run_task(spec.goal, ctx)
        status, err, summary = outcome.status, outcome.error, outcome.summary
        m = outcome.metrics

    skill_saved = None
    if status == "done" and record_skill_name and ctx.trace:
        from jarvis.agent.skills import record_skill

        skill = record_skill(record_skill_name, ctx.trace)
        path = cfg.skills_dir / f"{record_skill_name}.yaml"
        skill.save(path)
        skill_saved = str(path)

    checker = None
    if status == "done":
        final = _observe(backend)
        from jarvis.bench.checkers import run_checkers

        checker = run_checkers(spec.check, {
            "fs_root": fs_root, "desktop": desktop, "audit": audit, "metrics": m,
            "backend": backend, "final_screen": final,
        })
    audit.close()
    return {
        "task": spec.name, "arm": arm, "seed": seed, "planner": "skill" if skill_path else planner_mode,
        "status": status, "summary": summary, "error": err,
        "steps": m.get("steps", 0), "llm_calls": m.get("llm_calls", 0),
        "tokens": m.get("tokens", 0), "usd": m.get("usd", 0.0),
        "vlm_calls": m.get("vlm_calls", 0), "bytes_offdevice": m.get("bytes_offdevice", 0),
        "confirmations_shown": m.get("confirmations_shown", 0),
        "unsafe_blocked": m.get("unsafe_blocked", 0),
        "elapsed_s": round(time.monotonic() - t0, 3),
        "checker": checker,
        "checker_ok": bool(checker and checker["ok"]),
        "skill_saved": skill_saved,
    }


async def run_benchmark(cfg, task_paths: list[Path], planner_mode: str = "scripted", arms: list[str] | None = None, seeds: int = 3) -> list[dict]:
    arms = arms or ["A"]
    results = []
    for path in task_paths:
        spec = TaskSpec.load(path)
        for arm in arms:
            if arm == "C":
                results.append({"task": spec.name, "arm": arm, "status": "skipped", "error": "arm C (vision-only) requires the real Windows backend + VLM"})
                continue
            run_results = []
            skill_file = None
            for seed in range(seeds):
                if arm == "D" and seed > 0 and skill_file:
                    r = await run_spec(spec, cfg, planner_mode=planner_mode, arm=arm, seed=seed, skill_path=skill_file)
                elif arm == "D":
                    r = await run_spec(spec, cfg, planner_mode=planner_mode, arm=arm, seed=seed, record_skill_name=f"{spec.name}_skill")
                    skill_file = Path(r["skill_saved"]) if r.get("skill_saved") else None
                else:
                    r = await run_spec(spec, cfg, planner_mode=planner_mode, arm=arm, seed=seed)
                run_results.append(r)
            times = [r["elapsed_s"] for r in run_results]
            ok = [r["checker_ok"] for r in run_results]
            results.append({
                "task": spec.name, "arm": arm, "planner": planner_mode,
                "checker_success": sum(ok) / len(ok),
                "steps_p50": statistics.median([r["steps"] for r in run_results]),
                "time_p50": statistics.median(times),
                "time_p90": sorted(times)[int(0.9 * (len(times) - 1))],
                "llm_calls_avg": statistics.mean([r["llm_calls"] for r in run_results]),
                "usd_avg": statistics.mean([r["usd"] for r in run_results]),
                "confirmations_avg": statistics.mean([r["confirmations_shown"] for r in run_results]),
                "unsafe_blocked_avg": statistics.mean([r["unsafe_blocked"] for r in run_results]),
                "bytes_offdevice_avg": statistics.mean([r["bytes_offdevice"] for r in run_results]),
                "replay_determinism": all(r["status"] == run_results[0]["status"] for r in run_results),
                "runs": run_results,
            })
    return results


def print_report(results: list[dict]) -> str:
    lines = [f"{'task':24} {'arm':4} {'check':6} {'steps':6} {'time_p50':9} {'llm':4} {'usd':8} {'det':4}"]
    for r in results:
        if "checker_success" in r:
            lines.append(
                f"{r['task']:24} {r['arm']:4} {r['checker_success']:6.2f} {r['steps_p50']:<6} "
                f"{r['time_p50']:<9} {r['llm_calls_avg']:<4} {r['usd_avg']:<8.4f} {str(r['replay_determinism']):4}"
            )
        else:
            lines.append(f"{r['task']:24} {r['arm']:4} SKIP: {r.get('error', '')}")
    return "\n".join(lines)
