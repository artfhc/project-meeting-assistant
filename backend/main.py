"""
FastAPI application entry point for the Meeting Assistant backend.

Run from the repo root with:

    python -m uvicorn backend.main:app --host 127.0.0.1 --port 7357 --reload

The ``PYTHONPATH`` must include the repo root so that the existing modules
(``audio``, ``transcription``, ``summarization``, ``config``) are importable
without modification.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import jobs
from backend.db import get_all_settings, init_db
from backend.routers import (
    devices,
    meetings,
    recordings,
    settings,
    summaries,
    transcriptions,
    ws,
)

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    On startup:
      - Initialise the SQLite database (create tables if absent).
      - Load the Whisper model (blocking; happens once).
      - Initialise the OpenAI summarizer.

    On shutdown: nothing special is required.
    """
    # --- Startup ---
    logger.info("Initialising database…")
    await init_db()

    # Patch Config from DB settings before any module reads it.
    # Modules (WhisperTranscriber, OpenAISummarizer) capture Config attributes at
    # construction time, so this must happen first.
    logger.info("Applying user settings to Config…")
    from config.settings import Config

    db_settings = await get_all_settings()

    # API key — DB value wins over the env-var default when present.
    if db_settings.get("openai_api_key"):
        Config.OPENAI_API_KEY = db_settings["openai_api_key"]

    # Whisper model — fall back to the class default ('base') when absent.
    Config.WHISPER_MODEL = db_settings.get("whisper_model") or Config.WHISPER_MODEL

    # Output directories — only override when the user has explicitly set a path.
    output_dir = db_settings.get("output_dir")
    if output_dir:
        import os

        Config.OUTPUT_DIR = output_dir
        Config.AUDIO_DIR = os.path.join(output_dir, "audio")
        Config.TRANSCRIPT_DIR = os.path.join(output_dir, "transcripts")
        Config.SUMMARY_DIR = os.path.join(output_dir, "summaries")

    Config.create_directories()
    logger.info("Config patched — OUTPUT_DIR=%s  WHISPER_MODEL=%s", Config.OUTPUT_DIR, Config.WHISPER_MODEL)

    logger.info("Loading Whisper model (this may take a moment)…")
    try:
        from transcription.whisper_client import WhisperTranscriber

        jobs.whisper = WhisperTranscriber()
        logger.info("Whisper model loaded successfully")
    except Exception as exc:
        logger.error("Failed to load Whisper model: %s", exc)
        jobs.whisper = None

    logger.info("Initialising OpenAI summarizer…")
    try:
        from summarization.openai_summarizer import OpenAISummarizer

        jobs.summarizer = OpenAISummarizer()
        logger.info("OpenAI summarizer ready")
    except Exception as exc:
        logger.warning(
            "OpenAI summarizer could not be initialised (check API key): %s", exc
        )
        jobs.summarizer = None

    yield

    # --- Shutdown ---
    logger.info("Shutting down Meeting Assistant backend")


app = FastAPI(
    title="Meeting Assistant API",
    description="Backend API for the Meeting Assistant desktop application.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:7357",  # Same-origin requests
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(meetings.router)
app.include_router(recordings.router)
app.include_router(transcriptions.router)
app.include_router(summaries.router)
app.include_router(devices.router)
app.include_router(settings.router)
app.include_router(ws.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Lightweight liveness probe."""
    return {"status": "ok"}
