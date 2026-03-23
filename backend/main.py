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
from backend.db import init_db
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
