from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

from jarvis.safety.risk import classify, set_mcp_tiers
from jarvis.core.schema import Step

FIXTURE = Path(__file__).parent / "fixture_mcp_server.py"

MCP_READY = True
try:
    from mcp import ClientSession, StdioServerParameters  # noqa: F401
    from mcp.client.stdio import stdio_client  # noqa: F401
except ImportError:
    MCP_READY = False

pytestmark = pytest.mark.skipif(not MCP_READY, reason="mcp package not installed")


def step_action(tool: str, args: dict | None = None) -> Step:
    return Step(thought="t", action={"type": "connector_call", "tool": tool, "args": args or {}}, expect="e")


def _screen():
    from jarvis.core.schema import Screen

    return Screen(app="a", window_title="W")


def test_unknown_mcp_tool_defaults_tier3():
    r = classify(step_action("mcp.fixture.echo"), _screen())
    assert r.tier == 3 and not r.denied
    set_mcp_tiers({"mcp.fixture.echo": 0})
    try:
        r = classify(step_action("mcp.fixture.echo"), _screen())
        assert r.tier == 0
    finally:
        set_mcp_tiers({})


def test_registry_match_and_call(tmp_path):
    from jarvis.connectors.mcp_client import McpToolRegistry, call_named_tool

    cfg = tmp_path / "jarvis.toml"
    cfg.write_text(
        f'[mcp_servers.fixture]\ncommand = "{sys.executable}"\nargs = ["{FIXTURE}"]\n',
        encoding="utf-8",
    )
    registry = McpToolRegistry(cfg)
    asyncio.run(registry.connect())
    names = [t["name"] for t in registry.tools]
    assert "echo" in names and "add_numbers" in names

    matched = registry.match({"goal": "please echo hello world"})
    assert matched is not None and matched.action.tool == "mcp.fixture.echo"
    assert registry.match({"goal": "nothing relevant here"}) is None

    result = asyncio.run(registry.call("fixture", "echo", {"text": "hi"}))
    assert not result["is_error"] and "echo:hi" in result["content"]

    result2 = asyncio.run(call_named_tool("fixture", "add_numbers", {"a": 2, "b": 3}, cfg))
    assert "5" in str(result2["content"])

    with pytest.raises(KeyError):
        asyncio.run(registry.call("nope", "echo", {}))


def test_list_servers_from_root_toml():
    from jarvis.connectors.mcp_client import load_servers

    servers = load_servers(Path(__file__).parent.parent / "jarvis.toml")
    assert isinstance(servers, list)
