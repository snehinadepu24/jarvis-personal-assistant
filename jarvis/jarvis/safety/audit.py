from __future__ import annotations

import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path

BASE_COLS = (
    "ts REAL, task TEXT, step INTEGER, route TEXT, tier INTEGER, action TEXT, target_key TEXT, "
    "window TEXT, approved_by TEXT, result TEXT, model TEXT, tokens INTEGER, usd REAL, bytes_offdevice INTEGER"
)


class Audit:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
        try:
            self._conn.execute("PRAGMA journal_mode=WAL")
        except sqlite3.DatabaseError as error:
            self._conn.close()
            backup = self.path.with_name(
                f"{self.path.stem}.corrupt-{datetime.now():%Y%m%d-%H%M%S}{self.path.suffix}"
            )
            self.path.replace(backup)
            print(
                f"JARVIS WARNING: audit database was invalid ({error}); "
                f"preserved as {backup}",
                flush=True,
            )
            self._conn = sqlite3.connect(str(self.path), check_same_thread=False)
            self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute(f"CREATE TABLE IF NOT EXISTS audit ({BASE_COLS})")
        # Add new columns if missing
        self._ensure_column("input_mode", "TEXT DEFAULT 'semantic'")
        self._ensure_column("snapshot_id", "TEXT DEFAULT ''")
        self._conn.commit()

    def _ensure_column(self, col_name: str, col_type: str) -> None:
        try:
            self._conn.execute(f"ALTER TABLE audit ADD COLUMN {col_name} {col_type}")
        except Exception:
            pass  # column already exists

    def log(
        self,
        task: str = "",
        step: int | None = None,
        route: str = "",
        tier: int | None = None,
        action: str = "",
        target_key: str = "",
        window: str = "",
        approved_by: str = "",
        result: str = "",
        model: str = "",
        tokens: int = 0,
        usd: float = 0.0,
        bytes_offdevice: int = 0,
        input_mode: str = "semantic",
        snapshot_id: str = "",
    ) -> None:
        with self._lock:
            self._conn.execute(
                "INSERT INTO audit VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    time.time(),
                    task,
                    step,
                    route,
                    tier,
                    action,
                    target_key,
                    window,
                    approved_by,
                    result,
                    model,
                    tokens,
                    usd,
                    bytes_offdevice,
                    input_mode,
                    snapshot_id,
                ),
            )
            self._conn.commit()

    def rows(self, limit: int = 100) -> list[dict]:
        with self._lock:
            cur = self._conn.execute("SELECT * FROM audit ORDER BY rowid DESC LIMIT ?", (limit,))
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]

    def close(self) -> None:
        with self._lock:
            self._conn.close()
