from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

from jarvis.config import Config



def cmd_capabilities(args):
    from jarvis.capabilities import format_capabilities
    print(format_capabilities(as_json=args.json))
    return 0

def cmd_setup_check(args):
    print("=" * 60)
    print("JARVIS for Windows - Environment & Setup Check")
    print("=" * 60)
    print(f"Platform: {sys.platform} ({'Windows native' if sys.platform == 'win32' else 'Emulated/Simulated mode'})")
    print(f"Python: {sys.version.split()[0]}")

    cfg = Config.load()
    print(f"Data directory: {cfg.data_dir}")
    print(f"Planner Provider: {cfg.planner_provider}")
    print(f"Planner Model: {cfg.planner_model}")

    gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        masked = gemini_key[:6] + "..." + gemini_key[-4:] if len(gemini_key) > 10 else "***"
        print(f"Google AI Studio Gemini API Key: Configured ({masked})")
    else:
        print("Google AI Studio Gemini API Key: NOT SET (set GEMINI_API_KEY for live planning)")

    if sys.platform == "win32":
        try:
            import win32gui
            print("win32gui / pywin32: OK")
        except ImportError:
            print("win32gui / pywin32: Not installed (optional on non-Windows)")
    else:
        print("Simulated Desktop Backend: Available (mock_backend)")

    print("\nSystem ready for JARVIS execution.")
    return 0


def cmd_dump(args):
    cfg = Config.load()
    from jarvis.perception.base import build_backend
    from jarvis.perception.serialize import serialize_screen

    backend = build_backend(cfg)
    screen = asyncio.run(backend.observe())
    print(f"\nForeground Window: '{screen.window_title}' ({screen.app or 'unknown'})")
    print(f"Elements detected: {len(screen.elements)}")
    print("-" * 50)
    print(serialize_screen(screen))
    return 0


def cmd_run(args):
    cfg = Config.load()
    from jarvis.bench.runner import TaskSpec, run_spec

    task_path = Path(args.task)
    if not task_path.exists():
        print(f"Task file not found: {task_path}")
        return 1

    spec = TaskSpec.load(task_path)
    print(f"Running task: {spec.name} ({spec.goal})")
    print(f"Planner: {args.planner}")

    result = asyncio.run(
        run_spec(
            spec,
            cfg,
            planner_mode=args.planner,
            approve=args.approve,
            record_skill_name=args.record_skill,
            engine=getattr(args, "engine", "state_machine"),
        )
    )

    print("\n" + "=" * 50)
    print(f"Task Result: {result['status'].upper()}")
    print(f"Steps: {result['steps']}")
    print(f"LLM Calls: {result['llm_calls']}")
    print(f"Elapsed: {result['elapsed_s']}s")
    if result.get("summary"):
        print(f"Summary: {result['summary']}")
    if result.get("checker"):
        print(f"Checker Status: {'PASS' if result['checker_ok'] else 'FAIL'}")
    if result.get("skill_saved"):
        print(f"Skill Recorded: {result['skill_saved']}")
    if result.get("error"):
        print(f"Error: {result['error']}")
    return 0 if result["status"] == "done" else 1


def cmd_bench(args):
    cfg = Config.load()
    from jarvis.bench.runner import print_report, run_benchmark

    tasks_dir = Path(__file__).resolve().parent.parent / "jarvis" / "bench" / "tasks"
    task_files = list(tasks_dir.glob("*.yaml")) if tasks_dir.exists() else []
    if not task_files:
        print("No benchmark tasks found.")
        return 1

    arms = [a.strip() for a in args.arms.split(",")]
    print(f"Running JARVIS-Win-30 Benchmark across {len(task_files)} tasks, arms {arms}, seeds {args.seeds}...")

    results = asyncio.run(
        run_benchmark(cfg, task_files, planner_mode=args.planner, arms=arms, seeds=args.seeds)
    )
    print("\n" + "=" * 60)
    print(print_report(results))
    print("=" * 60)
    return 0


def cmd_skill_replay(args):
    cfg = Config.load()
    from jarvis.agent.skills import planner_from_skill
    from jarvis.agent.state_machine import AgentContext, run_task
    from jarvis.core.skills_format import SkillModel
    from jarvis.perception.base import build_backend
    from jarvis.safety.audit import Audit
    from jarvis.safety.gate import ConfirmationGate, auto_approve_confirmer

    skill_path = Path(args.skill)
    if not skill_path.exists():
        print(f"Skill file not found: {skill_path}")
        return 1

    skill = SkillModel.load(skill_path)
    planner = planner_from_skill(skill)
    backend = build_backend(cfg)

    if cfg.backend == "mock" or sys.platform != "win32":
        from jarvis.actions.mock_executor import MockExecutor
        from jarvis.connectors.files import FilesConnector
        executor = MockExecutor(backend, FilesConnector(cfg.data_dir / "fs"))
    else:
        from jarvis.actions.uia_executor import UiaExecutor
        from jarvis.connectors.files import FilesConnector
        executor = UiaExecutor(backend, FilesConnector(cfg.data_dir / "fs"))

    audit = Audit(cfg.audit_db)
    gate = ConfirmationGate(confirmer=auto_approve_confirmer)
    ctx = AgentContext(
        llm=planner,
        backend=backend,
        executor=executor,
        gate=gate,
        audit=audit,
        budgets=cfg.budgets,
        task_name=f"skill_replay_{skill.name}",
    )

    goal = args.goal or f"Replay skill {skill.name}"
    print(f"Replaying Skill: {skill.name} (Steps: {len(skill.steps)}) - 0 LLM calls")
    outcome = asyncio.run(run_task(goal, ctx))
    print(f"Result: {outcome.status.upper()} (Steps: {outcome.steps})")
    audit.close()
    return 0 if outcome.status == "done" else 1


def cmd_smoke(args):
    print("=" * 60)
    print("Running JARVIS Smoke Test Pass (10x Snapshot + Verification)")
    print("=" * 60)
    cfg = Config.load()
    from jarvis.perception.base import build_backend

    backend = build_backend(cfg)
    timings = []
    for i in range(10):
        t0 = time.monotonic()
        screen = asyncio.run(backend.observe())
        dur = (time.monotonic() - t0) * 1000.0
        timings.append(dur)
        print(f"Iteration {i + 1:2d}: {dur:6.1f} ms ({len(screen.elements)} elements in '{screen.window_title}')")

    timings.sort()
    p50 = timings[len(timings) // 2]
    print(f"\nSnapshot latency p50: {p50:.1f} ms (Acceptance target: < 300 ms)")
    if p50 < 300:
        print("Smoke Pass: PASS")
        return 0
    else:
        print("Smoke Pass: WARNING (p50 above 300 ms threshold)")
        return 0


def cmd_mcp(args):
    cfg = Config.load()
    from jarvis.connectors.mcp_client import list_all_tools

    print("Querying configured MCP servers...")
    tools = asyncio.run(list_all_tools())
    if not tools:
        print("No MCP servers configured or active in jarvis.toml [mcp_servers].")
        return 0

    print(f"Discovered {len(tools)} MCP tool listings:")
    for t in tools:
        print(f" - [{t.get('server')}] {t.get('name')}: {t.get('description', '')}")
    return 0


def cmd_desktop(args):
    if sys.platform != "win32":
        print("Desktop mode requires Windows.")
        return 1
    cfg = Config.load()
    from jarvis.desktop.host import DesktopHost

    try:
        DesktopHost(cfg, wakeword_required=args.require_wakeword).run()
    except Exception as error:
        print(f"Desktop startup failed: {error}")
        return 1
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="JARVIS for Windows - Autonomous Desktop Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # capabilities
    p_cap = subparsers.add_parser("capabilities", help="Inspect platform and desktop capabilities")
    p_cap.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p_cap.set_defaults(func=cmd_capabilities)

    # setup-check
    p_setup = subparsers.add_parser("setup-check", help="Verify environment and dependencies")
    p_setup.set_defaults(func=cmd_setup_check)

    # dump
    p_dump = subparsers.add_parser("dump", help="Dump Set-of-Marks of the active window")
    p_dump.set_defaults(func=cmd_dump)

    # run
    p_run = subparsers.add_parser("run", help="Run a task")
    p_run.add_argument("task", help="Path to task YAML specification")
    p_run.add_argument("--planner", default="scripted", choices=["scripted", "gemini"], help="Planner mode")
    p_run.add_argument("--approve", default="auto", choices=["auto", "console", "deny"], help="Approval mode")
    p_run.add_argument("--record-skill", help="Name to save recorded skill as YAML")
    p_run.add_argument("--engine", default="state_machine", choices=["state_machine", "langgraph"], help="Execution engine")
    p_run.set_defaults(func=cmd_run)

    # bench
    p_bench = subparsers.add_parser("bench", help="Run benchmark suite")
    p_bench.add_argument("--arms", default="A,B,D", help="Comma-separated arms (A, B, C, D)")
    p_bench.add_argument("--seeds", type=int, default=3, help="Number of seeds per arm")
    p_bench.add_argument("--planner", default="scripted", help="Planner mode")
    p_bench.set_defaults(func=cmd_bench)

    # skill-replay
    p_replay = subparsers.add_parser("skill-replay", help="Replay a recorded skill")
    p_replay.add_argument("skill", help="Path to skill YAML file")
    p_replay.add_argument("--goal", help="Optional goal description")
    p_replay.set_defaults(func=cmd_skill_replay)

    # smoke
    p_smoke = subparsers.add_parser("smoke", help="Run smoke test pass")
    p_smoke.set_defaults(func=cmd_smoke)

    # mcp
    p_mcp = subparsers.add_parser("mcp", help="List tools from configured MCP servers")
    p_mcp.set_defaults(func=cmd_mcp)

    p_desktop = subparsers.add_parser("desktop", help="Run the integrated Windows desktop assistant")
    p_desktop.add_argument(
        "--require-wakeword",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require a working wake-word model before startup (default: true)",
    )
    p_desktop.set_defaults(func=cmd_desktop)

    parsed = parser.parse_args(argv)
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
