from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jarvis.core.schema import Step
from jarvis.llm.base import LLMError


@dataclass(frozen=True)
class ServerConfig:
    name: str
    params: Any


def load_servers(config_path: Path | str | None = None) -> list[ServerConfig]:
    from mcp import StdioServerParameters

    path = Path(config_path) if config_path else (Path(__file__).resolve().parents[2] / "jarvis.toml")
    if not path.exists():
        return []
    raw = tomllib.loads(path.read_text(encoding="utf-8")).get("mcp_servers", {})
    out = []
    for name, item in raw.items():
        env = item.get("env")
        out.append(ServerConfig(name, StdioServerParameters(
            command=item["command"],
            args=list(item.get("args", [])),
            env=dict(env) if env else None,
            cwd=item.get("cwd"),
            encoding=item.get("encoding", "utf-8"),
            encoding_error_handler=item.get("encoding_error_handler", "strict"),
        )))
    return out


def tool_view(tool: Any) -> dict[str, Any]:
    return {"name": tool.name, "description": tool.description or "", "input_schema": tool.input_schema}


async def list_server_tools(server: ServerConfig) -> dict[str, Any]:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async with stdio_client(server.params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.discover()
            listing = await session.list_tools()
            return {"server": server.name, "tools": [tool_view(t) for t in listing.tools]}


async def call_server_tool(server: ServerConfig, tool_name: str, arguments: dict | None = None) -> dict[str, Any]:
    from mcp import ClientSession
    from mcp.client.stdio import stdio_client

    async with stdio_client(server.params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.discover()
            listing = await session.list_tools()
            if not any(t.name == tool_name for t in listing.tools):
                raise LLMError(f"tool {tool_name!r} is not exposed by {server.name!r}")
            result = await session.call_tool(tool_name, arguments or {})
            return {
                "server": server.name,
                "tool": tool_name,
                "is_error": result.is_error,
                "content": [getattr(block, "text", repr(block)) for block in result.content],
                "structured_content": result.structured_content,
            }


async def list_all_tools(config_path: Path | str | None = None) -> list[dict[str, Any]]:
    import anyio

    servers = load_servers(config_path)
    if not servers:
        return []
    return list(await anyio.gather.gather(*[list_server_tools(s) for s in servers])) if False else await _gather(list_server_tools(s) for s in servers)


async def _gather(coros):
    import asyncio

    results = await asyncio.gather(*coros, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]


async def call_named_tool(server_name: str, tool_name: str, arguments: dict | None = None, config_path: Path | str | None = None) -> dict[str, Any]:
    servers = {s.name: s for s in load_servers(config_path)}
    if server_name not in servers:
        raise KeyError(f"unknown MCP server: {server_name}")
    return await call_server_tool(servers[server_name], tool_name, arguments)


class McpToolRegistry:
    def __init__(self, config_path: Path | str | None = None):
        self.config_path = config_path
        self.tools: list[dict] = []

    async def connect(self) -> None:
        listings = await list_all_tools(self.config_path)
        self.tools = [t for listing in listings for t in listing["tools"] | [{"server": listing["server"]}]] if False else [
            {**t, "server": listing["server"]} for listing in listings for t in listing["tools"]
        ]

    def match(self, intent: dict) -> Step | None:
        goal = (intent.get("goal") or "").lower()
        for t in self.tools:
            name = t["name"].lower()
            tokens = {name, *name.split("_")}
            if any(len(tok) > 3 and tok in goal for tok in tokens):
                return Step(
                    thought=f"route 1: registered MCP tool {t['server']}.{t['name']}",
                    action={"type": "connector_call", "tool": f"mcp.{t['server']}.{t['name']}", "args": {}},
                    expect="tool result returned",
                )
        return None

    async def call(self, server: str, tool: str, args: dict) -> dict[str, Any]:
        return await call_named_tool(server, tool, args, self.config_path)
