from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any
from jarvis.core.schema import Screen, Step


def _serialize_val(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return {k: _serialize_val(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [_serialize_val(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize_val(v) for k, v in obj.items()}
    return obj


class SqliteCheckpointer:
    """Thread-isolated persistent state checkpointer for LangGraph execution with time-travel rewind."""

    def __init__(self, db_path: Path | str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._init_db()

    def _init_db(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS checkpoints (
                thread_id TEXT,
                checkpoint_id TEXT,
                parent_id TEXT,
                ts REAL,
                state_json TEXT,
                metadata_json TEXT,
                PRIMARY KEY (thread_id, checkpoint_id)
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_thread_ts ON checkpoints(thread_id, ts)"
        )
        self._conn.commit()

    def put(self, thread_id: str, checkpoint_id: str, state: dict, parent_id: str = "", metadata: dict | None = None) -> None:
        serialized = json.dumps(_serialize_val(state))
        meta_json = json.dumps(metadata or {})
        self._conn.execute(
            """
            INSERT INTO checkpoints (thread_id, checkpoint_id, parent_id, ts, state_json, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(thread_id, checkpoint_id) DO UPDATE SET
                ts=excluded.ts,
                state_json=excluded.state_json,
                metadata_json=excluded.metadata_json
            """,
            (thread_id, checkpoint_id, parent_id, time.time(), serialized, meta_json),
        )
        self._conn.commit()

    def get(self, thread_id: str, checkpoint_id: str | None = None) -> dict | None:
        if checkpoint_id:
            row = self._conn.execute(
                "SELECT state_json FROM checkpoints WHERE thread_id=? AND checkpoint_id=?",
                (thread_id, checkpoint_id),
            ).fetchone()
        else:
            row = self._conn.execute(
                "SELECT state_json FROM checkpoints WHERE thread_id=? ORDER BY ts DESC LIMIT 1",
                (thread_id,),
            ).fetchone()
        return json.loads(row[0]) if row else None

    def list(self, thread_id: str) -> list[dict]:
        cursor = self._conn.execute(
            "SELECT checkpoint_id, parent_id, ts, metadata_json FROM checkpoints WHERE thread_id=? ORDER BY ts ASC",
            (thread_id,),
        )
        return [
            {"checkpoint_id": r[0], "parent_id": r[1], "ts": r[2], "metadata": json.loads(r[3])}
            for r in cursor.fetchall()
        ]

    def rewind(self, thread_id: str, steps: int = 1) -> dict | None:
        """Time-travel rewind: roll back execution state by N checkpoints."""
        cursor = self._conn.execute(
            "SELECT checkpoint_id, state_json FROM checkpoints WHERE thread_id=? ORDER BY ts DESC LIMIT ?",
            (thread_id, steps + 1),
        )
        rows = cursor.fetchall()
        if len(rows) > steps:
            target_id, state_json = rows[steps]
            # Prune newer checkpoints to maintain a clean timeline
            newer_ids = [r[0] for r in rows[:steps]]
            self._conn.executemany(
                "DELETE FROM checkpoints WHERE thread_id=? AND checkpoint_id=?",
                [(thread_id, cid) for cid in newer_ids],
            )
            self._conn.commit()
            return json.loads(state_json)
        return None

