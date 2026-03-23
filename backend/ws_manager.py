"""
WebSocket connection manager.

Only a single frontend client is expected at a time (desktop app), so the
manager tracks one active connection.  Errors during broadcast are swallowed
so that a stale or closed socket never raises inside a background job.
"""

from __future__ import annotations

import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WSManager:
    """Manages a single active WebSocket connection."""

    def __init__(self) -> None:
        self.active: WebSocket | None = None

    async def connect(self, ws: WebSocket) -> None:
        """Accept *ws* and register it as the active connection."""
        await ws.accept()
        self.active = ws
        logger.info("WebSocket client connected")

    async def disconnect(self) -> None:
        """Deregister the active connection (does not close the socket)."""
        self.active = None
        logger.info("WebSocket client disconnected")

    async def broadcast(self, data: dict) -> None:
        """Send *data* as JSON to the active connection.

        Any exception (e.g. the socket already closed) is caught and logged
        so that callers — especially background jobs — are never interrupted.
        """
        if self.active is None:
            return
        try:
            await self.active.send_json(data)
        except Exception as exc:  # noqa: BLE001
            logger.warning("WebSocket broadcast failed: %s", exc)
            self.active = None


# Module-level singleton used throughout the application.
manager = WSManager()
