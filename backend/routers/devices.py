"""
Endpoint to enumerate audio input devices available on the host.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from backend.models import AudioDevice

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/audio", response_model=list[AudioDevice])
async def list_audio_devices() -> list[AudioDevice]:
    """Return all audio input devices reported by PyAudio.

    Filters to devices that have at least one input channel.  Returns an
    empty list if PyAudio cannot be initialised rather than raising (the
    frontend should handle the case gracefully).
    """
    try:
        import pyaudio  # imported here so the module loads even without pyaudio

        pa = pyaudio.PyAudio()
        devices: list[AudioDevice] = []

        try:
            device_count = pa.get_device_count()
            for i in range(device_count):
                try:
                    info = pa.get_device_info_by_index(i)
                    if info.get("maxInputChannels", 0) > 0:
                        devices.append(
                            AudioDevice(index=i, name=info["name"])
                        )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Could not query device %d: %s", i, exc)
        finally:
            pa.terminate()

        return devices

    except Exception as exc:
        logger.error("Failed to enumerate audio devices: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"Could not enumerate audio devices: {exc}",
        ) from exc
