"""
Endpoint to enqueue a summarization job for a meeting.
"""

from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import jobs
from backend.db import get_db, get_meeting_by_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/summaries", tags=["summaries"])


class SummaryRequest(BaseModel):
    meeting_id: str
    prompt_key: str | None = None


@router.post("", status_code=202)
async def enqueue_summary(body: SummaryRequest) -> dict:
    """Enqueue a summarization job for the given meeting.

    The meeting must exist and have a transcript (transcription must be
    complete).  The job runs in the background; progress is delivered via the
    WebSocket.

    Returns 404 if the meeting is not found.
    Returns 409 if the meeting has no transcript or is already being processed.
    Returns 503 if the summarizer is not yet initialised.
    """
    async with get_db() as conn:
        row = await get_meeting_by_id(conn, body.meeting_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if not row["transcript"]:
        raise HTTPException(
            status_code=409,
            detail="Meeting has no transcript. Complete transcription first.",
        )

    status = row["status"]
    if status in ("transcribing", "summarizing"):
        raise HTTPException(
            status_code=409,
            detail=f"Meeting is currently being processed (status: {status}).",
        )

    if jobs.summarizer is None:
        raise HTTPException(
            status_code=503,
            detail="Summarizer is not available. Check your OpenAI API key in settings.",
        )

    # Prefer the prompt_key supplied in the request body; fall back to the
    # value stored on the meeting record itself.
    effective_prompt_key = body.prompt_key or row["prompt_key"]

    asyncio.create_task(
        jobs.run_summarization_job(
            body.meeting_id, row["transcript"], effective_prompt_key
        )
    )

    logger.info("Summarization job enqueued for meeting %s", body.meeting_id)
    return {"status": "accepted", "meeting_id": body.meeting_id}
