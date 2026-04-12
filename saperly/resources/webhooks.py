from __future__ import annotations

from typing import Any, Dict, Optional

from .._types import DeliveryListResult, WebhookStats, WebhookTestResult
from ._base import AsyncBaseResource, BaseResource


class WebhooksResource(BaseResource):
    def deliveries(
        self,
        *,
        line_id: Optional[str] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> DeliveryListResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "event_type": event_type,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        data = self._client.request("GET", "/webhooks/deliveries", query=query)
        return DeliveryListResult.from_dict(data)

    def stats(self, *, line_id: Optional[str] = None) -> WebhookStats:
        query: Dict[str, Any] = {"line_id": line_id}
        data = self._client.request("GET", "/webhooks/stats", query=query)
        return WebhookStats.from_dict(data)

    def test(self, *, line_id: str) -> WebhookTestResult:
        body = {"line_id": line_id}
        data = self._client.request("POST", "/webhooks/test", body=body)
        return WebhookTestResult.from_dict(data)


class AsyncWebhooksResource(AsyncBaseResource):
    async def deliveries(
        self,
        *,
        line_id: Optional[str] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> DeliveryListResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "event_type": event_type,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        data = await self._client.request("GET", "/webhooks/deliveries", query=query)
        return DeliveryListResult.from_dict(data)

    async def stats(self, *, line_id: Optional[str] = None) -> WebhookStats:
        query: Dict[str, Any] = {"line_id": line_id}
        data = await self._client.request("GET", "/webhooks/stats", query=query)
        return WebhookStats.from_dict(data)

    async def test(self, *, line_id: str) -> WebhookTestResult:
        body = {"line_id": line_id}
        data = await self._client.request("POST", "/webhooks/test", body=body)
        return WebhookTestResult.from_dict(data)
