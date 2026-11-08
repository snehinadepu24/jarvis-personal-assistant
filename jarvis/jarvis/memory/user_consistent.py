from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any
from jarvis.memory.types import Fact, UserPreference


class UserConsistentMemory:
    """Tier 4: Long-term persistent user memory, preferences, app quirks, and habits."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_facts (
                k TEXT PRIMARY KEY,
                v TEXT,
                category TEXT,
                confidence REAL,
                ts REAL
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                k TEXT,
                scope TEXT,
                app_name TEXT,
                v TEXT,
                ts REAL,
                PRIMARY KEY (k, scope, app_name)
            )
            """
        )
        self._conn.commit()

    def set_fact(self, key: str, value: str, category: str = "general", confidence: float = 1.0) -> None:
        self._conn.execute(
            """
            INSERT INTO user_facts (k, v, category, confidence, ts)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(k) DO UPDATE SET
                v=excluded.v,
                category=excluded.category,
                confidence=excluded.confidence,
                ts=excluded.ts
            """,
            (key, value, category, confidence, time.time()),
        )
        self._conn.commit()

    def get_fact(self, key: str) -> str | None:
        row = self._conn.execute("SELECT v FROM user_facts WHERE k=?", (key,)).fetchone()
        return row[0] if row else None

    def list_facts(self, category: str | None = None) -> list[Fact]:
        if category:
            cursor = self._conn.execute("SELECT k, v, category, confidence, ts FROM user_facts WHERE category=?", (category,))
        else:
            cursor = self._conn.execute("SELECT k, v, category, confidence, ts FROM user_facts")
        return [Fact(k, v, cat, conf, ts) for k, v, cat, conf, ts in cursor.fetchall()]

    def set_preference(self, key: str, value: Any, scope: str = "global", app_name: str = "") -> None:
        val_str = json.dumps(value)
        self._conn.execute(
            """
            INSERT INTO user_preferences (k, scope, app_name, v, ts)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(k, scope, app_name) DO UPDATE SET
                v=excluded.v,
                ts=excluded.ts
            """,
            (key, scope, app_name, val_str, time.time()),
        )
        self._conn.commit()

    def get_preference(self, key: str, app_name: str = "") -> Any:
        # Check app-specific preference first
        if app_name:
            row = self._conn.execute(
                "SELECT v FROM user_preferences WHERE k=? AND scope='app' AND app_name=?",
                (key, app_name),
            ).fetchone()
            if row:
                return json.loads(row[0])

        # Fallback to global preference
        row = self._conn.execute(
            "SELECT v FROM user_preferences WHERE k=? AND scope='global'",
            (key,),
        ).fetchone()
        return json.loads(row[0]) if row else None

    def prompt_context(self) -> str:
        facts = self.list_facts()
        if not facts:
            return ""
        lines = [f"- {f.key}: {f.value}" for f in facts[:10]]
        return "User Facts & Preferences:\n" + "\n".join(lines)

