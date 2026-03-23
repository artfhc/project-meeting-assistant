"""
Endpoints to start and stop audio recordings.

``AudioRecorder`` is stateful (it holds an open PyAudio stream between
``start_recording`` and ``stop_recording``), so a single instance is kept as a
module-level variable for the lifetime of a recording session.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from audio.recorder import AudioRecorder
from backend.db import get_db, get_meeting_by_id, update_meeting

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recordings", tags=["recordings"])

# Active recorder — populated by POST /recordings/start, cleared on stop.
_active_recorder: AudioRecorder | None = None


class StartRecordingBody(BaseModel):
    meeting_id: str


class StopRecordingBody(BaseModel):
    meeting_id: str
    duration_s: int


@router.post("/start", status_code=200)
async def start_recording(body: StartRecordingBody) -> dict:
    """Begin capturing audio for *meeting_id*.

    Returns 409 if a recording is already in progress.
    Returns 404 if the meeting does not exist.
    """
    global _active_recorder  # noqa: PLW0603

    if _active_recorder is not None:
        raise HTTPException(
            status_code=409,
            detail="A recording is already in progress. Stop it before starting a new one.",
        )

    async with get_db() as conn:
        row = await get_meeting_by_id(conn, body.meeting_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Meeting not found")

    recorder = AudioRecorder()
    started = recorder.start_recording()
    if not started:
        raise HTTPException(
            status_code=500, detail="Failed to start audio recording"
        )

    _active_recorder = recorder

    async with get_db() as conn:
        await update_meeting(conn, body.meeting_id, status="recording")

    logger.info("Recording started for meeting %s", body.meeting_id)
    return {"status": "recording", "meeting_id": body.meeting_id}


@router.post("/stop", status_code=200)
async def stop_recording(body: StopRecordingBody) -> dict:
    """Stop the active recording and save the audio file.

    Returns 409 if no recording is currently in progress.
    Returns 404 if the meeting does not exist.
    """
    global _active_recorder  # noqa: PLW0603

    if _active_recorder is None:
        raise HTTPException(
            status_code=409, detail="No recording is currently in progress."
        )

    async with get_db() as conn:
        row = await get_meeting_by_id(conn, body.meeting_id)
        if row is None:
            _active_recorder = None
            raise HTTPException(status_code=404, detail="Meeting not found")

    audio_path = _active_recorder.stop_recording()
    _active_recorder = None

    if audio_path is None:
        logger.error(
            "stop_recording() returned None for meeting %s", body.meeting_id
        )
        async with get_db() as conn:
            await update_meeting(
                conn,
                body.meeting_id,
                status="error",
                error_msg="Recording stopped but no audio file was produced",
            )
        raise HTTPException(
            status_code=500, detail="Recording stopped but produced no audio file"
        )

    async with get_db() as conn:
        await update_meeting(
            conn,
            body.meeting_id,
            audio_path=audio_path,
            duration_s=body.duration_s,
            status="recorded",
        )

    logger.info(
        "Recording stopped for meeting %s → %s", body.meeting_id, audio_path
    )
    return {
        "status": "recorded",
        "meeting_id": body.meeting_id,
        "audio_path": audio_path,
        "duration_s": body.duration_s,
    }
