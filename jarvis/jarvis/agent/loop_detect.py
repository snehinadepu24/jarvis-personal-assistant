from __future__ import annotations

import hashlib
from collections import deque

WINDOW = 6
SAME_LIMIT = 3
EMPTY_DIFF_LIMIT = 3


class LoopDetector:
    def __init__(self):
        self._recent: deque[str] = deque(maxlen=WINDOW)
        self._empty_diffs: deque[bool] = deque(maxlen=EMPTY_DIFF_LIMIT)

    @staticmethod
    def action_hash(window_title: str, action_type: str, key: str, text: str) -> str:
        basis = f"{window_title}|{action_type}|{key}|{text}"
        return hashlib.blake2s(basis.encode(), digest_size=8).hexdigest()

    def record(self, window_title: str, action_type: str, key: str, text: str = "") -> None:
        self._recent.append(self.action_hash(window_title, action_type, key, text))

    def note_diff(self, empty: bool) -> None:
        self._empty_diffs.append(empty)

    def should_recover(self) -> bool:
        if len(self._recent) >= SAME_LIMIT:
            last = self._recent[-1]
            if sum(1 for h in self._recent if h == last) >= SAME_LIMIT:
                return True
        if len(self._empty_diffs) == EMPTY_DIFF_LIMIT and all(self._empty_diffs):
            return True
        return False

    def reset(self) -> None:
        self._recent.clear()
        self._empty_diffs.clear()
