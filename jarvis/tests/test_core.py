from __future__ import annotations

import time

import pytest

from jarvis.core.schema import Rect, Screen, Step, UiElement, element_key, step_schema
from jarvis.perception.diff import screen_diff
from jarvis.perception.router import KNOWN_OPAQUE, choose_route, uia_confidence
from jarvis.perception.serialize import serialize, serialize_screen


def el(mark, name="Save", aid="save-btn", ct=50000, patterns=("invoke",), value=None, **kw):
    return UiElement(
        mark=mark, role="button", name=name, value=value, automation_id=aid,
        control_type=ct, rect=Rect(l=10, t=10, r=90, b=40), enabled=True,
        patterns=list(patterns), key=element_key(aid, ct, name, "TestWindow"), **kw,
    )


def screen(elements, cls="TestWindow", title="Test"):
    return Screen(app="test", window_title=title, window_class=cls, hwnd=1, pid=2, elements=elements, coverage_ratio=0.8, ts=time.time())


def test_action_union_discriminated():
    s = Step(thought="t", action={"type": "click", "mark": 3, "reason": "r"}, expect="e")
    assert s.action.mark == 3
    s2 = Step(thought="t", action={"type": "toggle", "mark": 1, "desired": "off"}, expect="e")
    assert s2.action.desired == "off"
    with pytest.raises(Exception):
        Step(thought="t", action={"type": "nope"}, expect="e")


def test_step_schema_has_discriminator():
    schema = step_schema()
    assert "discriminator" in schema["properties"]["action"] or "anyOf" in schema["properties"]["action"]


def test_element_key_stable_and_distinct():
    a = element_key("x", 50000, "Save", "W")
    b = element_key("x", 50000, "Save", "W")
    c = element_key("y", 50000, "Save", "W")
    assert a == b and a != c


def test_serialize_line_format():
    block, tokens = serialize([el(1), el(2, name="Bluetooth", aid="bt", ct=50002, patterns=("toggle",))])
    line1 = block.splitlines()[0]
    assert line1.startswith("[1] button") and '"Save"' in line1 and "#save-btn" in line1 and "{invoke}" in line1
    assert tokens > 0


def test_serialize_password_value_never_emitted():
    e = el(1, name="pw", aid="pw", ct=50004, patterns=("value",), value="hunter2")
    e.is_password = True
    block, _ = serialize([e])
    assert "hunter2" not in block and "password" in block


def test_serialize_budget_truncates():
    elems = [el(i, name=f"elem-{i}", aid=f"a{i}") for i in range(1, 400)]
    block, tokens = serialize(elems, token_budget=1500)
    assert tokens <= 1500 + 40
    assert "use scroll" in block


def test_rank_and_marks_focused_first():
    from jarvis.perception.serialize import assign_marks, rank

    e1 = el(0, name="A")  # unfocused button
    e2 = el(0, name="B", focused=True)
    ordered = assign_marks(rank([e1, e2]))
    assert ordered[0].name == "B" and ordered[0].mark == 1


def test_diff_added_removed_changed():
    s1 = screen([el(1, aid="a"), el(2, aid="b")])
    s2 = screen([el(1, aid="a"), el(3, aid="c")])
    d = screen_diff(s1, s2)
    assert d.added == [el(3, aid="c").key]
    assert d.removed == [el(2, aid="b").key]
    assert not d.empty


def test_diff_changed_value():
    k = el(1, aid="a")
    s1 = screen([k])
    changed = el(1, aid="a", value="new text")
    s2 = screen([changed])
    d = screen_diff(s1, s2)
    assert d.changed == [k.key]


def test_confidence_formula():
    s = screen([el(1), el(2, name="Bluetooth", aid="bt", ct=50002, patterns=("toggle",))])
    c = uia_confidence(s)
    assert 0.0 <= c <= 1.0
    empty = screen([])
    assert uia_confidence(empty) == 0.0


def test_confidence_opaque_penalty():
    good = screen([el(1), el(2, name="x", aid="x", ct=50004, patterns=("value",))])
    opaque = screen([el(1), el(2, name="x", aid="x", ct=50004, patterns=("value",))], cls=list(KNOWN_OPAQUE)[0])
    assert uia_confidence(opaque) < uia_confidence(good)


def test_choose_route_rules():
    assert choose_route(0.7)[0] == 2
    assert choose_route(0.4)[0] == 3
    assert choose_route(0.7, verify_failures=2)[0] == 3
    assert choose_route(0.4, verify_failures=2, route3_failures=2, allow_vlm=True)[0] == 4
    assert choose_route(0.4, verify_failures=2, route3_failures=2, allow_vlm=False)[0] == 3
