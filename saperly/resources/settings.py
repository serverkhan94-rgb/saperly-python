from __future__ import annotations

from typing import Any, Dict, Optional

from .._types import Settings
from ._base import AsyncBaseResource, BaseResource


class SettingsResource(BaseResource):
    def get(self) -> Settings:
        data = self._client.request("GET", "/settings")
        return Settings.from_dict(data)

    def update(self, *, default_webhook_url: Optional[str] = None) -> Settings:
        body: Dict[str, Any] = {}
        if default_webhook_url is not None:
            body["default_webhook_url"] = default_webhook_url
        data = self._client.request("PATCH", "/settings", body=body)
        return Settings.from_dict(data)


class AsyncSettingsResource(AsyncBaseResource):
    async def get(self) -> Settings:
        data = await self._client.request("GET", "/settings")
        return Settings.from_dict(data)

    async def update(self, *, default_webhook_url: Optional[str] = None) -> Settings:
        body: Dict[str, Any] = {}
        if default_webhook_url is not None:
            body["default_webhook_url"] = default_webhook_url
        data = await self._client.request("PATCH", "/settings", body=body)
        return Settings.from_dict(data)
