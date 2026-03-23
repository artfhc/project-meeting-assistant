"""
SQLite database layer for the Meeting Assistant backend.

All operations use aiosqlite for non-blocking async I/O.  The database file
lives at ~/.meeting-assistant/meeting_assistant.db and is created automatically
on first startup.
"""

from __future__ import annotations

import aiosqlite
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

DB_PATH: Path = Path.home() / ".meeting-assistant" / "meeting_assistant.db"

_CREATE_MEETINGS_TABLE = """
CREATE TABLE IF NOT EXISTS meetings (
    id              TEXT    PRIMARY KEY,
    title           TEXT    NOT NULL DEFAULT '',
    created_at      TEXT    NOT NULL,
    duration_s      INTEGER,
    audio_path      TEXT,
    transcript_path TEXT,
    summary_path    TEXT,
    transcript      TEXT,
    summary         TEXT,
    prompt_key      TEXT,
    status          TEXT    NOT NULL DEFAULT 'created',
    error_msg       TEXT
);
"""

_CREATE_MEETINGS_INDEX = """
CREATE INDEX IF NOT EXISTS idx_meetings_created_at ON meetings (created_at DESC);
"""

_CREATE_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


async def init_db() -> None:
    """Create all tables and indexes if they do not already exist."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(_CREATE_MEETINGS_TABLE)
        await conn.execute(_CREATE_MEETINGS_INDEX)
        await conn.execute(_CREATE_SETTINGS_TABLE)
        await conn.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager that yields an open aiosqlite connection.

    The connection is configured to return rows as sqlite3.Row objects so
    columns can be accessed by name.
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn


# ---------------------------------------------------------------------------
# Settings helpers
# ---------------------------------------------------------------------------


async def get_setting(key: str, default: str = "") -> str:
    """Return the value stored for *key*, or *default* if absent."""
    async with get_db() as conn:
        async with conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ) as cursor:
            row = await cursor.fetchone()
            return row["value"] if row else default


async def set_setting(key: str, value: str) -> None:
    """Upsert *key* = *value* in the settings table."""
    async with get_db() as conn:
        await conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await conn.commit()


async def get_all_settings() -> dict[str, str]:
    """Return every row in the settings table as a plain dict."""
    async with get_db() as conn:
        async with conn.execute("SELECT key, value FROM settings") as cursor:
            rows = await cursor.fetchall()
            return {row["key"]: row["value"] for row in rows}


# ---------------------------------------------------------------------------
# Meeting helpers shared across routers
# ---------------------------------------------------------------------------


async def get_meeting_by_id(
    conn: aiosqlite.Connection, meeting_id: str
) -> aiosqlite.Row | None:
    """Fetch a single meeting row by primary key, or None if not found."""
    async with conn.execute(
        "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
    ) as cursor:
        return await cursor.fetchone()


async def update_meeting(
    conn: aiosqlite.Connection, meeting_id: str, **fields: object
) -> None:
    """Partially update a meeting row with the provided keyword arguments.

    Only non-None values are written; None means "leave unchanged".
    """
    if not fields:
        return
    set_clauses = ", ".join(f"{col} = ?" for col in fields)
    values = list(fields.values()) + [meeting_id]
    await conn.execute(
        f"UPDATE meetings SET {set_clauses} WHERE id = ?",  # noqa: S608
        values,
    )
    await conn.commit()
