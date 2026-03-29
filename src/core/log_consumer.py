import asyncio
import logging
import ssl
from typing import Optional

import websockets

from src.core.log_parser import parse_log_line
from src.core.tracker import IPTracker

logger = logging.getLogger(__name__)

RECONNECT_DELAY = 15


class LogConsumer:
    """Async WebSocket consumer for Marzban log streams.

    Maintains one connection per endpoint (main server + each node).
    Auto-reconnects with backoff on disconnection.
    """

    def __init__(self, tracker: IPTracker):
        self._tracker = tracker
        self._tasks: list[asyncio.Task] = []
        self._running = False

    async def start(self, ws_urls: list[tuple[str, Optional[int]]]):
        """Start consuming logs from all endpoints.

        Args:
            ws_urls: List of (ws_url, node_id) tuples.
                     node_id is None for the main server.
        """
        self._running = True
        for ws_url, node_id in ws_urls:
            label = f"node-{node_id}" if node_id else "main"
            task = asyncio.create_task(
                self._consume_loop(ws_url, label), name=f"log-consumer-{label}"
            )
            self._tasks.append(task)
        logger.info("Started %d log consumer(s)", len(self._tasks))

    async def stop(self):
        """Stop all consumer tasks."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        logger.info("All log consumers stopped")

    async def _consume_loop(self, ws_url: str, label: str):
        """Consume loop with auto-reconnect."""
        while self._running:
            try:
                await self._consume(ws_url, label)
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._running:
                    logger.warning(
                        "[%s] WebSocket disconnected: %s. Reconnecting in %ds...",
                        label,
                        e,
                        RECONNECT_DELAY,
                    )
                    await asyncio.sleep(RECONNECT_DELAY)

    async def _consume(self, ws_url: str, label: str):
        """Connect and consume messages from a single WebSocket."""
        logger.info("[%s] Connecting to log stream...", label)
        ssl_ctx = None
        if ws_url.startswith("wss://"):
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
        async with websockets.connect(
            ws_url,
            ssl=ssl_ctx,
            ping_interval=20,
            ping_timeout=30,
            close_timeout=5,
            additional_headers={"User-Agent": "MarzGuard/1.0"},
        ) as ws:
            logger.info("[%s] Connected to log stream", label)
            async for message in ws:
                if not self._running:
                    break
                self._process_message(str(message), label)

    def _process_message(self, message: str, label: str):
        """Parse a log message and feed into tracker."""
        for line in message.strip().split("\n"):
            if not line:
                continue
            entry = parse_log_line(line)
            if entry:
                logger.debug("[%s] Tracked: %s -> %s", label, entry.username, entry.source_ip)
                self._tracker.record(entry.username, entry.source_ip)
            elif "email" in line.lower():
                logger.debug("[%s] Unparsed line with email: %s", label, line[:200])
