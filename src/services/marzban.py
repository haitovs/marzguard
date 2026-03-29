import logging
from typing import Any, Optional

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)


class MarzbanClient:
    """Async client for the Marzban REST API."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.marzban_base_url.rstrip("/")
        self._username = settings.marzban_username
        self._password = settings.marzban_password
        self._token: Optional[str] = None
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            verify=False,
        )

    async def close(self):
        await self._client.aclose()

    async def _authenticate(self) -> str:
        """Authenticate with Marzban and obtain a JWT token."""
        resp = await self._client.post(
            "/api/admin/token",
            data={
                "username": self._username,
                "password": self._password,
                "grant_type": "password",
            },
        )
        resp.raise_for_status()
        self._token = resp.json()["access_token"]
        logger.info("Authenticated with Marzban panel")
        return self._token

    async def _get_token(self) -> str:
        if not self._token:
            await self._authenticate()
        return self._token

    async def _request(
        self, method: str, path: str, retry_auth: bool = True, **kwargs
    ) -> httpx.Response:
        """Make an authenticated request, re-authenticating on 401."""
        token = await self._get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"

        resp = await self._client.request(method, path, headers=headers, **kwargs)

        if resp.status_code == 401 and retry_auth:
            await self._authenticate()
            headers["Authorization"] = f"Bearer {self._token}"
            resp = await self._client.request(method, path, headers=headers, **kwargs)

        resp.raise_for_status()
        return resp

    async def get_users(self, offset: int = 0, limit: int = 100) -> dict[str, Any]:
        """List users from Marzban."""
        resp = await self._request(
            "GET", "/api/users", params={"offset": offset, "limit": limit}
        )
        return resp.json()

    async def get_user(self, username: str) -> dict[str, Any]:
        """Get a single user's details."""
        resp = await self._request("GET", f"/api/user/{username}")
        return resp.json()

    async def modify_user(self, username: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update a user (used for enable/disable)."""
        resp = await self._request("PUT", f"/api/user/{username}", json=data)
        return resp.json()

    async def disable_user(self, username: str) -> dict[str, Any]:
        """Disable a user by setting status to disabled."""
        logger.warning("Disabling user: %s", username)
        return await self.modify_user(username, {"status": "disabled"})

    async def enable_user(self, username: str) -> dict[str, Any]:
        """Re-enable a user by setting status to active."""
        logger.info("Re-enabling user: %s", username)
        return await self.modify_user(username, {"status": "active"})

    async def get_nodes(self) -> list[dict[str, Any]]:
        """List all configured nodes."""
        resp = await self._request("GET", "/api/nodes")
        return resp.json()

    async def get_log_ws_url(self, node_id: Optional[int] = None) -> str:
        """Get the WebSocket URL for log streaming."""
        token = await self._get_token()
        if node_id is not None:
            return f"{self._ws_base}/api/node/{node_id}/logs?token={token}"
        return f"{self._ws_base}/api/core/logs?token={token}"

    @property
    def _ws_base(self) -> str:
        """Convert HTTP base URL to WebSocket URL."""
        return self.base_url.replace("https://", "wss://").replace("http://", "ws://")

    async def get_all_log_ws_urls(self) -> list[tuple[str, Optional[int]]]:
        """Get WebSocket URLs for main server and all nodes.

        Returns list of (ws_url, node_id) tuples. node_id is None for main server.
        """
        token = await self._get_token()
        urls = [(f"{self._ws_base}/api/core/logs?token={token}", None)]

        try:
            nodes = await self.get_nodes()
            for node in nodes:
                node_id = node.get("id")
                if node_id and node.get("status") == "connected":
                    url = f"{self._ws_base}/api/node/{node_id}/logs?token={token}"
                    urls.append((url, node_id))
        except Exception as e:
            logger.warning("Failed to fetch nodes: %s", e)

        return urls
