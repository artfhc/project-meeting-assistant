"""
Endpoints to start and stop audio recordings.

``AudioRecorder`` is stateful (it holds an open PyAudio stream between
``start_recording`` and ``stop_recording``), so a single instance is kept as a
module-level variable for the lifetime of a recording session.
"""

from __future__ import annotations

import logging
import threading

import pyaudio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from audio.recorder import AudioRecorder
from config.settings import Config
from backend.db import get_all_settings, get_db, get_meeting_by_id, update_meeting

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recordings", tags=["recordings"])

# Active recorder — populated by POST /recordings/start, cleared on stop.
# Typed as AudioRecorder because DeviceAwareRecorder is defined below; at
# runtime the stored instance will always be a DeviceAwareRecorder.
_active_recorder: AudioRecorder | None = None


# ---------------------------------------------------------------------------
# DeviceAwareRecorder
# ---------------------------------------------------------------------------


class DeviceAwareRecorder(AudioRecorder):
    """AudioRecorder subclass that honours a caller-supplied device index.

    ``AudioRecorder.start_recording`` always calls ``self.audio.open()``
    without an ``input_device_index`` argument, which locks recording to the
    system default device.  This subclass overrides ``start_recording`` to
    forward the chosen device index to PyAudio when one has been specified.

    The parent class must not be modified (it lives in ``audio/recorder.py``),
    so the override duplicates the minimal stream-open logic.  All other
    behaviour (frame capture, file saving, cleanup) is inherited unchanged.

    NOTE: Changing the Whisper model requires a backend restart because
    ``WhisperTranscriber`` loads the model at construction time.  Changing the
    audio device index does *not* require a restart — it is read from the DB
    on each ``POST /recordings/start`` call.
    """

    def __init__(self, device_index: int = -1) -> None:
        self._device_index = device_index
        super().__init__()

    def start_recording(self) -> bool:  # type: ignore[override]
        """Start audio recording, optionally using *device_index*."""
        if self.is_recording:
            return False

        self.frames = []
        self.is_recording = True

        open_kwargs: dict = {
            "format": pyaudio.paInt16,
            "channels": Config.CHANNELS,
            "rate": Config.SAMPLE_RATE,
            "input": True,
            "frames_per_buffer": Config.CHUNK_SIZE,
        }
        if self._device_index >= 0:
            open_kwargs["input_device_index"] = self._device_index

        self.stream = self.audio.open(**open_kwargs)

        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.start()

        return True


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

    # Read the audio device preference from the settings DB.  A value of -1
    # (the default) means "use the system default input device".
    settings_dict = await get_all_settings()
    device_idx = int(settings_dict.get("audio_device_index") or -1)

    recorder = DeviceAwareRecorder(device_index=device_idx)
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
