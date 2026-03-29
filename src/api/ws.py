import asyncio
import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt

from src.config import get_settings
from src.core.tracker import IPTracker
from src.dependencies import get_tracker

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manage active WebSocket connections for live dashboard."""

    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.remove(ws)


manager = ConnectionManager()


@router.websocket("/ws/live")
async def live_dashboard(websocket: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    # Authenticate via query param
    token = websocket.query_params.get("token", "")
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if not payload.get("sub"):
            await websocket.close(code=4001, reason="Unauthorized")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    tracker = get_tracker()
    await manager.connect(websocket)

    try:
        while True:
            # Send snapshot every 5 seconds
            snapshot = tracker.get_all_active()
            data = {
                "type": "snapshot",
                "users": {
                    username: {"ips": ips, "count": len(ips)}
                    for username, ips in snapshot.items()
                },
                "total_users": len(snapshot),
                "total_ips": sum(len(ips) for ips in snapshot.values()),
            }
            await websocket.send_json(data)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
