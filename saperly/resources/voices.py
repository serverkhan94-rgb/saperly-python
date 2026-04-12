from __future__ import annotations

from .._types import VoiceListResult
from ._base import AsyncBaseResource, BaseResource


class VoicesResource(BaseResource):
    def list(self) -> VoiceListResult:
        data = self._client.request("GET", "/voices")
        return VoiceListResult.from_dict(data)


class AsyncVoicesResource(AsyncBaseResource):
    async def list(self) -> VoiceListResult:
        data = await self._client.request("GET", "/voices")
        return VoiceListResult.from_dict(data)
