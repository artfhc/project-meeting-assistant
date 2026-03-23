"""
Endpoint to enqueue a transcription job for a meeting.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import jobs
from backend.db import get_db, get_meeting_by_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transcriptions", tags=["transcriptions"])


class TranscriptionRequest(BaseModel):
    meeting_id: str


@router.post("", status_code=202)
async def enqueue_transcription(body: TranscriptionRequest) -> dict:
    """Enqueue a transcription job for the given meeting.

    The meeting must exist and have an ``audio_path`` set (i.e. a recording
    must have been completed).  The job runs in the background; progress is
    delivered via the WebSocket.

    Returns 404 if the meeting is not found.
    Returns 409 if the meeting has no audio file or is already being processed.
    """
    async with get_db() as conn:
        row = await get_meeting_by_id(conn, body.meeting_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if not row["audio_path"]:
        raise HTTPException(
            status_code=409,
            detail="Meeting has no audio file. Complete a recording first.",
        )

    status = row["status"]
    if status in ("transcribing", "summarizing"):
        raise HTTPException(
            status_code=409,
            detail=f"Meeting is currently being processed (status: {status}).",
        )

    if jobs.whisper is None:
        raise HTTPException(
            status_code=503,
            detail="Whisper model is not loaded. Server may still be starting up.",
        )

    asyncio.create_task(
        jobs.run_transcription_job(body.meeting_id, row["audio_path"])
    )

    logger.info("Transcription job enqueued for meeting %s", body.meeting_id)
    return {"status": "accepted", "meeting_id": body.meeting_id}
