from fastapi import APIRouter

from src.api import auth, dashboard, logs, policies, settings, users, webhooks, ws

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(policies.router)
api_router.include_router(dashboard.router)
api_router.include_router(settings.router)
api_router.include_router(logs.router)
api_router.include_router(webhooks.router)

# WS router is mounted directly on the app (no /api/v1 prefix)
ws_router = ws.router
