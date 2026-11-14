from __future__ import annotations

import hashlib
import time
import uuid
from enum import Enum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class ActionErrorCode(str, Enum):
    INVALID_ARGS = "INVALID_ARGS"
    NOT_FOUND = "NOT_FOUND"
    STALE_TARGET = "STALE_TARGET"
    AMBIGUOUS_TARGET = "AMBIGUOUS_TARGET"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    UNSUPPORTED = "UNSUPPORTED"
    TIMEOUT = "TIMEOUT"
    ACTION_FAILED = "ACTION_FAILED"
    SAFETY_BLOCKED = "SAFETY_BLOCKED"


class ErrorDisposition(BaseModel):
    retry: bool = False
    requires_observe: bool = False


class ActionError(BaseModel):
    code: ActionErrorCode
    disposition: ErrorDisposition = Field(default_factory=ErrorDisposition)
    suggestion: str = ""
    detail: str = ""


class ActionEnvelope(BaseModel):
    version: str = "1.0"
    ok: bool = True
    command: str = ""
    data: dict = Field(default_factory=dict)
    error: ActionError | None = None


class Rect(BaseModel):
    l: int
    t: int
    r: int
    b: int

    @property
    def w(self) -> int:
        return self.r - self.l

    @property
    def h(self) -> int:
        return self.b - self.t

    def center(self) -> tuple[int, int]:
        return (self.l + self.r) // 2, (self.t + self.b) // 2

    def area(self) -> int:
        return max(0, self.w) * max(0, self.h)


class UiElement(BaseModel):
    mark: int
    role: str
    name: str = ""
    value: str | None = None
    automation_id: str = ""
    class_name: str = ""
    control_type: int
    rect: Rect
    enabled: bool
    focused: bool = False
    offscreen: bool = False
    is_password: bool = False
    patterns: list[str] = []
    state: dict[str, str] = {}
    key: str
    selector: list[dict] = []
    source: Literal["uia", "ocr", "detector", "vlm"] = "uia"
    ref: str = ""


class Screen(BaseModel):
    platform: Literal["windows", "android"] = "windows"
    app: str = ""
    window_title: str = ""
    window_class: str = ""
    hwnd: int = 0
    pid: int = 0
    integrity: str = "medium"
    elements: list[UiElement] = []
    focused_mark: int | None = None
    coverage_ratio: float = 0.0
    screenshot_hash: str | None = None
    ts: float = 0.0
    snapshot_id: str = ""
    snapshot_ts: float = 0.0

    def ensure_snapshot_id(self) -> str:
        if not self.snapshot_id:
            self.snapshot_id = f"s_{uuid.uuid4().hex[:8]}"
            if not self.snapshot_ts:
                self.snapshot_ts = time.time()
        for e in self.elements:
            if not e.ref and e.mark:
                e.ref = f"@{self.snapshot_id}:e{e.mark}"
        return self.snapshot_id

    def ref_for(self, mark: int) -> str:
        sid = self.ensure_snapshot_id()
        return f"@{sid}:e{mark}"

    def by_mark(self, mark: int) -> UiElement | None:
        return next((e for e in self.elements if e.mark == mark), None)

    def by_key(self, key: str) -> UiElement | None:
        return next((e for e in self.elements if e.key == key), None)

    def by_ref(self, ref: str) -> UiElement | None:
        self.ensure_snapshot_id()
        for e in self.elements:
            if e.ref == ref:
                return e
        # If ref is formatted like @snapshot:e<mark> or just e<mark>
        if ":e" in ref:
            try:
                mark = int(ref.split(":e")[-1])
                return self.by_mark(mark)
            except ValueError:
                pass
        return None


class _A(BaseModel):
    reason: str = Field(default="", max_length=200)
    ref: str | None = None
    snapshot_id: str | None = None


class Click(_A):
    type: Literal["click", "double_click", "right_click"]
    mark: int | None = None


class SetText(_A):
    type: Literal["type"]
    mark: int | None = None
    text: str
    submit: bool = False


class Clear(_A):
    type: Literal["clear"]
    mark: int | None = None


class SelectItem(_A):
    type: Literal["select_item"]
    mark: int | None = None
    item: str | None = None


class Toggle(_A):
    type: Literal["toggle"]
    mark: int | None = None
    desired: Literal["on", "off"] | None = None


class Expand(_A):
    type: Literal["expand", "collapse"]
    mark: int | None = None


class Scroll(_A):
    type: Literal["scroll"]
    mark: int | None = None
    direction: Literal["up", "down", "left", "right"]


class Hotkey(_A):
    type: Literal["hotkey"]
    keys: str


class FocusWindow(_A):
    type: Literal["focus_window"]
    title_contains: str


class OpenApp(_A):
    type: Literal["open_app"]
    name: str


class OpenUrl(_A):
    type: Literal["open_url"]
    url: str


class RunPS(_A):
    type: Literal["run_powershell"]
    script: str


class Connector(_A):
    type: Literal["connector_call"]
    tool: str
    args: dict = {}


class Wait(_A):
    type: Literal["wait"]
    seconds: float = Field(le=10)


class AskUser(_A):
    type: Literal["ask_user"]
    question: str


class Done(_A):
    type: Literal["done"]
    summary: str


class Fail(_A):
    type: Literal["fail"]
    why: str


Action = Annotated[
    Union[
        Click, SetText, Clear, SelectItem, Toggle, Expand, Scroll, Hotkey, FocusWindow,
        OpenApp, OpenUrl, RunPS, Connector, Wait, AskUser, Done, Fail,
    ],
    Field(discriminator="type"),
]


class Step(BaseModel):
    thought: str = Field(default='', max_length=2000)
    action: Action
    expect: str = Field(default='', max_length=1000)
    input_mode: Literal["semantic", "physical"] = "semantic"
    snapshot_id: str | None = None


class AskUserPending(Exception):
    def __init__(self, question: str):
        super().__init__(question)
        self.question = question


CONTROL_TYPES = {
    50000: "Button", 50001: "Calendar", 50002: "CheckBox", 50003: "ComboBox",
    50004: "Edit", 50005: "Hyperlink", 50006: "Image", 50007: "ListItem",
    50008: "List", 50009: "Menu", 50010: "MenuBar", 50011: "MenuItem",
    50012: "ProgressBar", 50013: "RadioButton", 50014: "ScrollBar", 50015: "Slider",
    50016: "Spinner", 50017: "StatusBar", 50018: "Tab", 50019: "TabItem",
    50020: "Text", 50021: "Thumb", 50023: "Tree", 50024: "TreeItem",
    50025: "Custom", 50026: "Group", 50027: "Thumb", 50028: "DataGrid",
    50029: "DataItem", 50030: "Document", 50031: "SplitButton", 50032: "Window",
    50033: "Pane",
}

ROLE = {
    50000: "button", 50002: "checkbox", 50003: "combobox", 50004: "edit", 50005: "link",
    50007: "listitem", 50008: "list", 50011: "menuitem", 50013: "radio", 50018: "tab",
    50019: "tabitem", 50020: "text", 50024: "treeitem", 50025: "custom", 50026: "group",
    50029: "dataitem", 50030: "document", 50032: "window", 50033: "pane",
}


def element_key(aid: str, ct: int, name: str, win_class: str) -> str:
    basis = f"{win_class}|{aid}|{ct}|{'' if aid else name}"
    return hashlib.blake2s(basis.encode(), digest_size=8).hexdigest()


def step_schema() -> dict:
    return Step.model_json_schema()
