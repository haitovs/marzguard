import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.router import api_router, ws_router
from src.config import get_settings
from src.core.enforcer import Enforcer
from src.core.log_consumer import LogConsumer
from src.core.scheduler import create_scheduler
from src.core.tracker import IPTracker
from src.dependencies import set_tracker
from src.models.database import get_session_factory, init_db
from src.services.marzban import MarzbanClient
from src.services.notify import NotificationDispatcher

logger = logging.getLogger("marzguard")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    settings = get_settings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Ensure data directory exists
    db_url = settings.database_url
    if "sqlite" in db_url:
        db_path = db_url.split("///")[-1]
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize core components
    tracker = IPTracker(ttl_seconds=settings.ip_ttl_seconds)
    set_tracker(tracker)

    marzban = MarzbanClient()
    notifier = NotificationDispatcher()
    await notifier.init()

    session_factory = get_session_factory()
    enforcer = Enforcer(tracker, marzban, notifier, session_factory)

    # Set marzban client on users API
    from src.api.users import set_marzban
    set_marzban(marzban)

    # Start log consumer — collect node IPs to filter them from tracking
    node_ips: set[str] = set()
    try:
        nodes = await marzban.get_nodes()
        for node in nodes:
            addr = node.get("address", "")
            if addr:
                node_ips.add(addr)
        if node_ips:
            logger.info("Node IPs to filter: %s", node_ips)
    except Exception as e:
        logger.warning("Failed to fetch node IPs: %s", e)

    log_consumer = LogConsumer(tracker, node_ips=node_ips)
    try:
        ws_urls = await marzban.get_all_log_ws_urls()
        await log_consumer.start(ws_urls)
        logger.info("Log consumer started with %d endpoint(s)", len(ws_urls))
    except Exception as e:
        logger.error("Failed to start log consumer: %s", e)
        logger.info("Continuing without log streaming — configure Marzban connection in .env")

    # Start scheduler
    scheduler = create_scheduler(tracker, enforcer)
    scheduler.start()
    logger.info("Scheduler started")

    logger.info("MarzGuard started successfully")

    yield

    # Shutdown
    scheduler.shutdown(wait=False)
    await log_consumer.stop()
    await marzban.close()
    await notifier.close()
    logger.info("MarzGuard shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="MarzGuard",
        description="IP limit management for Marzban proxy panel",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Rate limiting
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # API routes
    app.include_router(api_router)
    app.include_router(ws_router)

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "service": "marzguard"}

    # Serve frontend SPA
    ui_dir = Path(__file__).parent / "ui" / "dist"
    if ui_dir.exists() and (ui_dir / "index.html").exists():
        app.mount("/assets", StaticFiles(directory=ui_dir / "assets"), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            file_path = ui_dir / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            return FileResponse(ui_dir / "index.html")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )
