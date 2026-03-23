"""
WebSocket endpoint.

The frontend connects here to receive real-time job progress updates.  The
server does not process messages sent by the client; the receive loop simply
keeps the connection alive until the client disconnects.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.ws_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket) -> None:
    """Accept a WebSocket connection and hold it open for push notifications."""
    await manager.connect(ws)
    try:
        while True:
            # Drain any incoming frames so the connection stays healthy.
            # We do not act on client messages.
            await ws.receive_text()
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
    except Exception as exc:  # noqa: BLE001
        logger.warning("WebSocket connection closed unexpectedly: %s", exc)
    finally:
        await manager.disconnect()
