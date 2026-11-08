from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from jarvis.core.schema import (
    ActionEnvelope,
    ActionError,
    ActionErrorCode,
    ErrorDisposition,
    Step,
)


@dataclass
class ActionResult:
    ok: bool
    detail: str = ""
    artifact: dict = field(default_factory=dict)
    envelope: ActionEnvelope | None = None
    input_mode: Literal["semantic", "physical"] = "semantic"

    @classmethod
    def success(
        cls,
        command: str = "",
        data: dict | None = None,
        detail: str = "",
        artifact: dict | None = None,
        input_mode: Literal["semantic", "physical"] = "semantic",
    ) -> ActionResult:
        data = data or {}
        artifact = artifact or {}
        envelope = ActionEnvelope(
            version="1.0",
            ok=True,
            command=command,
            data=data,
            error=None,
        )
        return cls(
            ok=True,
            detail=detail or f"{command}: ok",
            artifact=artifact,
            envelope=envelope,
            input_mode=input_mode,
        )

    @classmethod
    def failure(
        cls,
        command: str = "",
        code: ActionErrorCode = ActionErrorCode.ACTION_FAILED,
        detail: str = "",
        suggestion: str = "",
        retry: bool = False,
        requires_observe: bool = False,
        artifact: dict | None = None,
        input_mode: Literal["semantic", "physical"] = "semantic",
    ) -> ActionResult:
        artifact = artifact or {}
        error = ActionError(
            code=code,
            disposition=ErrorDisposition(retry=retry, requires_observe=requires_observe),
            suggestion=suggestion,
            detail=detail,
        )
        envelope = ActionEnvelope(
            version="1.0",
            ok=False,
            command=command,
            data={},
            error=error,
        )
        return cls(
            ok=False,
            detail=detail or f"{command} failed: {code.value}",
            artifact=artifact,
            envelope=envelope,
            input_mode=input_mode,
        )

    @classmethod
    def stale_target(
        cls,
        command: str = "",
        ref: str = "",
        snapshot_id: str = "",
        suggestion: str = "Take a fresh UIA snapshot and retry with its target ref.",
        artifact: dict | None = None,
    ) -> ActionResult:
        detail = f"Target ref {ref!r} from snapshot {snapshot_id!r} is stale or target element has moved."
        return cls.failure(
            command=command,
            code=ActionErrorCode.STALE_TARGET,
            detail=detail,
            suggestion=suggestion,
            retry=True,
            requires_observe=True,
            artifact=artifact,
            input_mode="semantic",
        )


class Executor(Protocol):
    name: str

    async def apply(self, step: Step, screen=None) -> ActionResult: ...
