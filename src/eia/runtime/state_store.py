"""SQLite state store for live contact budget, consent, and quiet hours."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path


DEFAULT_DB_PATH = Path("data/eia_state.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS contact_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    contact_budget INTEGER NOT NULL DEFAULT 2,
    contacts_today INTEGER NOT NULL DEFAULT 0,
    last_contact_ts TEXT,
    quiet_hours_start INTEGER NOT NULL DEFAULT 22,
    quiet_hours_end INTEGER NOT NULL DEFAULT 8,
    consent_telegram INTEGER NOT NULL DEFAULT 0,
    last_reset_date TEXT
);
INSERT OR IGNORE INTO contact_state (id) VALUES (1);
"""


@dataclass
class ContactState:
    """Snapshot of live contact governor persistence."""

    contact_budget: int = 2
    contacts_today: int = 0
    last_contact_ts: datetime | None = None
    quiet_hours_start: int = 22
    quiet_hours_end: int = 8
    consent_telegram: bool = False
    last_reset_date: date | None = None


class StateStore:
    """SQLite-backed contact budget and consent flags."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA)
            conn.commit()

    def load(self) -> ContactState:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM contact_state WHERE id = 1").fetchone()
        if row is None:
            return ContactState()
        last_ts = (
            datetime.fromisoformat(row["last_contact_ts"])
            if row["last_contact_ts"]
            else None
        )
        reset = (
            date.fromisoformat(row["last_reset_date"])
            if row["last_reset_date"]
            else None
        )
        return ContactState(
            contact_budget=row["contact_budget"],
            contacts_today=row["contacts_today"],
            last_contact_ts=last_ts,
            quiet_hours_start=row["quiet_hours_start"],
            quiet_hours_end=row["quiet_hours_end"],
            consent_telegram=bool(row["consent_telegram"]),
            last_reset_date=reset,
        )

    def save(self, state: ContactState) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE contact_state SET
                    contact_budget = ?,
                    contacts_today = ?,
                    last_contact_ts = ?,
                    quiet_hours_start = ?,
                    quiet_hours_end = ?,
                    consent_telegram = ?,
                    last_reset_date = ?
                WHERE id = 1
                """,
                (
                    state.contact_budget,
                    state.contacts_today,
                    state.last_contact_ts.isoformat() if state.last_contact_ts else None,
                    state.quiet_hours_start,
                    state.quiet_hours_end,
                    int(state.consent_telegram),
                    state.last_reset_date.isoformat() if state.last_reset_date else None,
                ),
            )
            conn.commit()

    def reset_daily_budget_if_needed(self, today: date | None = None) -> ContactState:
        """Roll contacts_today at UTC midnight boundary."""
        today = today or datetime.now(timezone.utc).date()
        state = self.load()
        if state.last_reset_date != today:
            state.contacts_today = 0
            state.last_reset_date = today
            self.save(state)
        return state

    def enable_telegram_consent(self) -> ContactState:
        state = self.load()
        state.consent_telegram = True
        self.save(state)
        return state

    def record_contact(self, ts: datetime | None = None) -> ContactState:
        state = self.reset_daily_budget_if_needed()
        state.contacts_today += 1
        state.last_contact_ts = ts or datetime.now(timezone.utc)
        self.save(state)
        return state

    def set_quiet_hours(self, start: int, end: int) -> ContactState:
        state = self.load()
        state.quiet_hours_start = start
        state.quiet_hours_end = end
        self.save(state)
        return state
