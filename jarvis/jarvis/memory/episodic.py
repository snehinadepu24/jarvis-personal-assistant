from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from jarvis.memory.types import EpisodicRecord


class EpisodicMemory:
    """Tier 3: Past task execution history, trajectories, and outcomes via SQLite + FTS5."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS episodes (
                task_id TEXT PRIMARY KEY,
                goal TEXT,
                steps_json TEXT,
                status TEXT,
                summary TEXT,
                error TEXT,
                duration_s REAL,
                recovery_count INTEGER,
                created_at REAL
            )
            """
        )
        # Attempt FTS5 creation
        self._has_fts = True
        try:
            self._conn.execute(
                """
                CREATE VIRTUAL TABLE IF NOT EXISTS episodes_fts USING fts5(
                    task_id,
                    goal,
                    summary
                )
                """
            )
        except Exception:
            self._has_fts = False
        self._conn.commit()

    def record_episode(self, record: EpisodicRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO episodes (task_id, goal, steps_json, status, summary, error, duration_s, recovery_count, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(task_id) DO UPDATE SET
                steps_json=excluded.steps_json,
                status=excluded.status,
                summary=excluded.summary,
                error=excluded.error,
                duration_s=excluded.duration_s,
                recovery_count=excluded.recovery_count
            """,
            (
                record.task_id,
                record.goal,
                record.steps_json,
                record.status,
                record.summary,
                record.error,
                record.duration_s,
                record.recovery_count,
                record.created_at,
            ),
        )
        if self._has_fts:
            try:
                self._conn.execute(
                    "INSERT INTO episodes_fts (task_id, goal, summary) VALUES (?, ?, ?)",
                    (record.task_id, record.goal, record.summary),
                )
            except Exception:
                pass
        self._conn.commit()

    def query_similar(self, query: str, limit: int = 3) -> list[EpisodicRecord]:
        tokens = [w.strip() for w in query.split() if len(w.strip()) > 2]
        if not tokens:
            return []

        results: list[EpisodicRecord] = []
        if self._has_fts:
            try:
                clean_q = " OR ".join(f'"{t}"' for t in tokens[:6])
                cursor = self._conn.execute(
                    """
                    SELECT e.task_id, e.goal, e.steps_json, e.status, e.summary, e.error, e.duration_s, e.recovery_count, e.created_at
                    FROM episodes e
                    JOIN episodes_fts f ON e.task_id = f.task_id
                    WHERE episodes_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                    """,
                    (clean_q, limit),
                )
                for row in cursor.fetchall():
                    results.append(EpisodicRecord(*row))
                if results:
                    return results
            except Exception:
                pass

        # Fallback LIKE matching
        like_clauses = " OR ".join(["goal LIKE ?" for _ in tokens[:4]])
        params = [f"%{t}%" for t in tokens[:4]] + [limit]
        cursor = self._conn.execute(
            f"SELECT task_id, goal, steps_json, status, summary, error, duration_s, recovery_count, created_at FROM episodes WHERE {like_clauses} ORDER BY created_at DESC LIMIT ?",
            params,
        )
        for row in cursor.fetchall():
            results.append(EpisodicRecord(*row))
        return results

    def get_latest(self, limit: int = 5) -> list[EpisodicRecord]:
        cursor = self._conn.execute(
            "SELECT task_id, goal, steps_json, status, summary, error, duration_s, recovery_count, created_at FROM episodes ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [EpisodicRecord(*row) for row in cursor.fetchall()]

