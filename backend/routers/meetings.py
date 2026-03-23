"""
CRUD endpoints for meeting records.

Meeting IDs use the ``YYYYmmdd_HHMMSS`` format to match the existing naming
convention used by the audio recorder and transcriber.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException

from backend.db import get_db, get_meeting_by_id, update_meeting
from backend.models import Meeting, MeetingCreate, MeetingUpdate

router = APIRouter(prefix="/meetings", tags=["meetings"])


def _row_to_meeting(row) -> Meeting:
    """Convert a sqlite3.Row to a ``Meeting`` model."""
    return Meeting(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        duration_s=row["duration_s"],
        audio_path=row["audio_path"],
        transcript_path=row["transcript_path"],
        summary_path=row["summary_path"],
        transcript=row["transcript"],
        summary=row["summary"],
        prompt_key=row["prompt_key"],
        status=row["status"],
        error_msg=row["error_msg"],
    )


@router.get("", response_model=list[Meeting])
async def list_meetings() -> list[Meeting]:
    """Return all meetings ordered newest-first."""
    async with get_db() as conn:
        async with conn.execute(
            "SELECT * FROM meetings ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
    return [_row_to_meeting(r) for r in rows]


@router.post("", response_model=Meeting, status_code=201)
async def create_meeting(body: MeetingCreate) -> Meeting:
    """Create a new meeting record and return it."""
    meeting_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    created_at = datetime.utcnow().isoformat()

    async with get_db() as conn:
        await conn.execute(
            """
            INSERT INTO meetings (id, title, created_at, prompt_key, status)
            VALUES (?, ?, ?, ?, 'created')
            """,
            (meeting_id, body.title, created_at, body.prompt_key),
        )
        await conn.commit()
        row = await get_meeting_by_id(conn, meeting_id)

    if row is None:
        raise HTTPException(status_code=500, detail="Failed to create meeting")
    return _row_to_meeting(row)


@router.get("/{meeting_id}", response_model=Meeting)
async def get_meeting(meeting_id: str) -> Meeting:
    """Return a single meeting by ID."""
    async with get_db() as conn:
        row = await get_meeting_by_id(conn, meeting_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return _row_to_meeting(row)


@router.patch("/{meeting_id}", response_model=Meeting)
async def patch_meeting(meeting_id: str, body: MeetingUpdate) -> Meeting:
    """Update the title and/or prompt_key of a meeting."""
    updates: dict[str, object] = {}
    if body.title is not None:
        updates["title"] = body.title
    if body.prompt_key is not None:
        updates["prompt_key"] = body.prompt_key

    async with get_db() as conn:
        row = await get_meeting_by_id(conn, meeting_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Meeting not found")
        if updates:
            await update_meeting(conn, meeting_id, **updates)
        row = await get_meeting_by_id(conn, meeting_id)

    return _row_to_meeting(row)  # type: ignore[arg-type]


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: str) -> None:
    """Delete a meeting record (files on disk are not removed)."""
    async with get_db() as conn:
        row = await get_meeting_by_id(conn, meeting_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Meeting not found")
        await conn.execute("DELETE FROM meetings WHERE id = ?", (meeting_id,))
        await conn.commit()
