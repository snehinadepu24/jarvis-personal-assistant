from __future__ import annotations

import tomllib
from pathlib import Path

from jarvis.llm.base import est_tokens


class Costs:
    def __init__(self, prices_path: Path | None = None):
        path = prices_path or Path(__file__).parent / "prices.toml"
        self.prices: dict[str, dict] = {}
        if path.exists():
            self.prices = tomllib.loads(path.read_text(encoding="utf-8"))
        self.prices.pop("note", None)

    def usd(self, model: str, input_tokens: int, output_tokens: int) -> float:
        p = self.prices.get(model)
        if not p:
            return 0.0
        return (input_tokens / 1e6) * p.get("input", 0.0) + (output_tokens / 1e6) * p.get("output", 0.0)

    def usage(self, model: str, prompt_text: str, reply_text: str, latency_ms: float):
        from jarvis.llm.base import Usage

        it, ot = est_tokens(prompt_text), est_tokens(reply_text)
        return Usage(
            model=model,
            input_tokens=it,
            output_tokens=ot,
            latency_ms=latency_ms,
            usd=self.usd(model, it, ot),
        )


COSTS = Costs()
