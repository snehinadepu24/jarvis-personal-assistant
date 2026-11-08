from __future__ import annotations

import sqlite3
import time
from pathlib import Path

MAX_WORDS = 120


class ProgressMemory:
    def __init__(self):
        self._facts: list[str] = []
        self._last_rewrite = 0

    def add(self, fact: str) -> None:
        self._facts.append(fact)
        self._facts = self._facts[-12:]

    def text(self) -> str:
        return " ".join(self._facts)[-1400:]

    def condense(self, step_no: int) -> None:
        if step_no - self._last_rewrite >= 5 and len(self._facts) > 3:
            seen, out = set(), []
            for f in self._facts:
                k = f.lower()[:60]
                if k not in seen:
                    seen.add(k)
                    out.append(f)
            self._facts = out[-8:]
            self._last_rewrite = step_no

    def words(self) -> int:
        return len(self.text().split())


class UserFacts:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._conn = sqlite3.connect(str(self.path))
        self._conn.execute("CREATE TABLE IF NOT EXISTS facts (k TEXT PRIMARY KEY, v TEXT, ts REAL)")
        self._conn.commit()

    def set(self, k: str, v: str) -> None:
        self._conn.execute(
            "INSERT INTO facts VALUES (?,?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v, ts=excluded.ts",
            (k, v, time.time()),
        )
        self._conn.commit()

    def get(self, k: str) -> str | None:
        row = self._conn.execute("SELECT v FROM facts WHERE k=?", (k,)).fetchone()
        return row[0] if row else None
