from __future__ import annotations

from mcp.server.mcpserver import MCPServer

srv = MCPServer("fixture")


def echo(text: str) -> str:
    """Return the text prefixed with echo:"""
    return f"echo:{text}"


def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


srv.add_tool(echo, name="echo", description="echo the given text")
srv.add_tool(add, name="add_numbers", description="add two numbers")

if __name__ == "__main__":
    srv.run()
