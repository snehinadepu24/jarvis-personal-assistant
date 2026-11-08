from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Budgets:
    steps: int = 25
    llm_calls: int = 40
    usd: float = 0.50
    seconds: float = 300
    vlm: int = 3


class BudgetExceeded(RuntimeError):
    def __init__(self, which: str):
        super().__init__(f"budget exceeded: {which}")
        self.which = which


def check_budget(b: Budgets, *, steps: int, llm_calls: int, usd: float, seconds: float, vlm: int) -> None:
    if steps > b.steps:
        raise BudgetExceeded(f"steps {steps}/{b.steps}")
    if llm_calls > b.llm_calls:
        raise BudgetExceeded(f"llm {llm_calls}/{b.llm_calls}")
    if usd > b.usd:
        raise BudgetExceeded(f"usd {usd:.2f}/{b.usd:.2f}")
    if seconds > b.seconds:
        raise BudgetExceeded(f"seconds {seconds:.0f}/{b.seconds:.0f}")
    if vlm > b.vlm:
        raise BudgetExceeded(f"vlm {vlm}/{b.vlm}")
