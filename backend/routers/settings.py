"""
Endpoints to read and write persistent application settings.

Settings are stored in the SQLite ``settings`` table.  When a key is absent
from the database the value is derived from the ``Config`` class (which reads
the ``.env`` file), providing a seamless migration path from the old
file-only configuration approach.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from config.settings import Config
from backend.db import get_all_settings, set_setting
from backend.models import SettingsModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])

# Mapping from SettingsModel field names to Config attribute names.
# Used to fill in defaults when a key has not yet been written to the DB.
_CONFIG_DEFAULTS: dict[str, object] = {
    "openai_api_key": Config.OPENAI_API_KEY,
    "whisper_model": Config.WHISPER_MODEL,
    "audio_device_index": -1,
    "output_dir": Config.OUTPUT_DIR,
    "default_prompt_key": "",
    "theme": "dark",
}


@router.get("", response_model=SettingsModel)
async def get_settings() -> SettingsModel:
    """Return current settings.

    Values missing from the database are filled in from ``Config`` defaults
    (which themselves fall back to ``.env``).
    """
    stored = await get_all_settings()

    def _get(key: str) -> str:
        return stored.get(key, str(_CONFIG_DEFAULTS.get(key, "")))

    return SettingsModel(
        openai_api_key=_get("openai_api_key"),
        whisper_model=_get("whisper_model"),
        audio_device_index=int(_get("audio_device_index") or -1),
        output_dir=_get("output_dir"),
        default_prompt_key=_get("default_prompt_key"),
        theme=_get("theme"),
    )


@router.put("", response_model=SettingsModel)
async def put_settings(body: SettingsModel) -> SettingsModel:
    """Persist all settings fields to the database.

    After saving, live-patches ``Config`` for values that take effect
    immediately without a restart:
      - ``OPENAI_API_KEY`` — used by every subsequent summarization call.
      - ``OPENAI_MODEL``   — used by every subsequent summarization call.

    ``WHISPER_MODEL`` is **not** hot-reloaded here because ``WhisperTranscriber``
    loads the model binary at construction time; a backend restart is required
    for that change to take effect.

    ``output_dir`` is also not hot-reloaded mid-session to avoid a situation
    where the first half of a recording goes to one directory and the summary
    to another.  A restart picks it up cleanly.
    """
    import os

    fields: dict[str, str] = {
        "openai_api_key": body.openai_api_key,
        "whisper_model": body.whisper_model,
        "audio_device_index": str(body.audio_device_index),
        "output_dir": body.output_dir,
        "default_prompt_key": body.default_prompt_key,
        "theme": body.theme,
    }
    for key, value in fields.items():
        await set_setting(key, value)

    # Live-patch Config for values that are safe to change at runtime.
    if body.openai_api_key:
        Config.OPENAI_API_KEY = body.openai_api_key

    # Apply output_dir change and recreate directories so that the new paths
    # exist before the next recording/transcription/summarization job runs.
    if body.output_dir:
        Config.OUTPUT_DIR = body.output_dir
        Config.AUDIO_DIR = os.path.join(body.output_dir, "audio")
        Config.TRANSCRIPT_DIR = os.path.join(body.output_dir, "transcripts")
        Config.SUMMARY_DIR = os.path.join(body.output_dir, "summaries")

    Config.create_directories()

    logger.info("Settings updated and Config patched")
    return body


@router.get("/prompts")
async def list_prompts() -> list[str]:
    """Return the available prompt template keys from ``config/prompts.yaml``.

    The frontend uses this list to populate the *Default Prompt Key* dropdown
    so users can only select keys that actually exist.
    """
    prompts = Config.get_summarization_prompts()
    return list(prompts.keys())
