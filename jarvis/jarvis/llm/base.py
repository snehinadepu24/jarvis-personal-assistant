from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Usage:
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0
    usd: float = 0.0

    def add(self, other: "Usage") -> None:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.latency_ms += other.latency_ms
        self.usd += other.usd


@dataclass
class TaskUsage:
    calls: int = 0
    usage: Usage = field(default_factory=Usage)
    vlm_calls: int = 0
    bytes_offdevice: int = 0

    def record(self, u: Usage) -> None:
        self.calls += 1
        self.usage.add(u)


class LLMError(RuntimeError):
    pass


def est_tokens(*texts: str) -> int:
    return sum(len(t) for t in texts if t) // 4


def extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LLMError(f"no JSON object in reply: {text[:120]!r}")
    return json.loads(text[start : end + 1])


class PlannerLLM(Protocol):
    name: str

    async def complete_json(
        self, system: str, messages: list[dict], schema: dict, *, thinking: str = "low"
    ) -> tuple[dict, Usage]: ...
