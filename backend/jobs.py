"""
Background job runners for transcription and summarization.

Both jobs are designed to be launched with ``asyncio.create_task`` from a
router and then run to completion independently.  Progress is pushed to the
connected WebSocket client via ``ws_manager.manager``.

Blocking library calls (Whisper, OpenAI) are offloaded to a thread pool via
``loop.run_in_executor`` so the event loop stays responsive.

The ``whisper`` and ``summarizer`` singletons are set by ``main.py`` during
the lifespan startup hook.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Callable

from transcription.whisper_client import WhisperTranscriber
from transcription.cleaner import TranscriptCleaner
from summarization.openai_summarizer import OpenAISummarizer

from backend.db import get_db, update_meeting
from backend import ws_manager as _ws_module

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Singletons — populated by main.py lifespan
# ---------------------------------------------------------------------------

whisper: WhisperTranscriber | None = None
summarizer: OpenAISummarizer | None = None


# ---------------------------------------------------------------------------
# Transcription job
# ---------------------------------------------------------------------------


async def run_transcription_job(meeting_id: str, audio_path: str) -> None:
    """Transcribe *audio_path* and persist results for *meeting_id*.

    Stages broadcast over WebSocket:
      - ``transcribing`` (0 → 95 %): Whisper chunked progress
      - ``cleaning``     (95 %):      transcript post-processing
      - ``done``         (100 %):     complete
      - ``error``        (0 %):       on any failure
    """
    job_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()

    # ----- 1. Mark meeting as transcribing -----
    async with get_db() as conn:
        await update_meeting(conn, meeting_id, status="transcribing")

    # ----- 2. Build progress callback (called from worker thread) -----
    def _progress_callback(message: str, progress: int) -> None:
        payload = {
            "type": "job_progress",
            "job_id": job_id,
            "meeting_id": meeting_id,
            "stage": "transcribing",
            "progress": progress,
            "message": message,
        }
        asyncio.run_coroutine_threadsafe(
            _ws_module.manager.broadcast(payload), loop
        )

    # ----- 3. Run Whisper in thread pool -----
    try:
        transcript_text, transcript_filepath = await loop.run_in_executor(
            None,
            lambda: whisper.transcribe_audio(audio_path, _progress_callback),  # type: ignore[union-attr]
        )
    except Exception as exc:
        logger.exception("Whisper transcription failed for meeting %s", meeting_id)
        await _handle_job_error(job_id, meeting_id, str(exc))
        return

    # transcribe_audio returns (None, error_string) on failure
    if transcript_text is None:
        error_msg = transcript_filepath or "Transcription returned no text"
        await _handle_job_error(job_id, meeting_id, error_msg)
        return

    # ----- 4. Clean transcript (fast, kept on event loop) -----
    await _ws_module.manager.broadcast(
        {
            "type": "job_progress",
            "job_id": job_id,
            "meeting_id": meeting_id,
            "stage": "cleaning",
            "progress": 95,
            "message": "Cleaning transcript…",
        }
    )
    cleaned_text: str = TranscriptCleaner.clean_transcript(transcript_text)

    # ----- 5. Persist results -----
    async with get_db() as conn:
        await update_meeting(
            conn,
            meeting_id,
            transcript=cleaned_text,
            transcript_path=transcript_filepath,
            status="transcribed",
        )

    # ----- 6. Broadcast completion -----
    await _ws_module.manager.broadcast(
        {
            "type": "job_progress",
            "job_id": job_id,
            "meeting_id": meeting_id,
            "stage": "done",
            "progress": 100,
            "message": "Transcription complete.",
        }
    )
    logger.info("Transcription job %s finished for meeting %s", job_id, meeting_id)


# ---------------------------------------------------------------------------
# Summarization job
# ---------------------------------------------------------------------------


async def run_summarization_job(
    meeting_id: str,
    transcript: str,
    prompt_key: str | None,
) -> None:
    """Summarize *transcript* for *meeting_id* using OpenAI.

    *prompt_key* is passed through to ``OpenAISummarizer.summarize_transcript``
    as the ``custom_prompt`` argument when provided.

    Stages broadcast over WebSocket:
      - ``summarizing`` (0 %):   job started
      - ``done``        (100 %): complete
      - ``error``       (0 %):   on any failure
    """
    job_id = str(uuid.uuid4())
    loop = asyncio.get_event_loop()

    # ----- 1. Mark meeting as summarizing -----
    async with get_db() as conn:
        await update_meeting(conn, meeting_id, status="summarizing")

    # ----- 2. Broadcast start -----
    await _ws_module.manager.broadcast(
        {
            "type": "job_progress",
            "job_id": job_id,
            "meeting_id": meeting_id,
            "stage": "summarizing",
            "progress": 0,
            "message": "Generating summary…",
        }
    )

    # ----- 3. Run OpenAI call in thread pool -----
    try:
        summary_text, summary_filepath = await loop.run_in_executor(
            None,
            lambda: summarizer.summarize_transcript(transcript, prompt_key),  # type: ignore[union-attr]
        )
    except Exception as exc:
        logger.exception("Summarization failed for meeting %s", meeting_id)
        await _handle_job_error(job_id, meeting_id, str(exc))
        return

    # summarize_transcript returns (None, error_string) on failure
    if summary_text is None:
        error_msg = summary_filepath or "Summarization returned no text"
        await _handle_job_error(job_id, meeting_id, error_msg)
        return

    # ----- 4. Persist results -----
    async with get_db() as conn:
        await update_meeting(
            conn,
            meeting_id,
            summary=summary_text,
            summary_path=summary_filepath,
            status="done",
        )

    # ----- 5. Broadcast completion -----
    await _ws_module.manager.broadcast(
        {
            "type": "job_progress",
            "job_id": job_id,
            "meeting_id": meeting_id,
            "stage": "done",
            "progress": 100,
            "message": "Summary complete.",
        }
    )
    logger.info("Summarization job %s finished for meeting %s", job_id, meeting_id)


# ---------------------------------------------------------------------------
# Shared error helper
# ---------------------------------------------------------------------------


async def _handle_job_error(job_id: str, meeting_id: str, error_msg: str) -> None:
    """Persist error state and broadcast the failure to the WebSocket client."""
    logger.error(
        "Job %s failed for meeting %s: %s", job_id, meeting_id, error_msg
    )
    async with get_db() as conn:
        await update_meeting(
            conn, meeting_id, status="error", error_msg=error_msg
        )
    await _ws_module.manager.broadcast(
        {
            "type": "job_progress",
            "job_id": job_id,
            "meeting_id": meeting_id,
            "stage": "error",
            "progress": 0,
            "message": error_msg,
        }
    )
