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
    """Persist all settings fields to the database."""
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

    logger.info("Settings updated")
    return body
