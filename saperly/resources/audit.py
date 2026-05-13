from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._types import UnifiedAuditResult
from ._base import AsyncBaseResource, BaseResource


class AuditResource(BaseResource):
    def list(
        self,
        *,
        api_key_id: str = "self",
        limit: Optional[int] = None,
        event_types: Optional[List[str]] = None,
    ) -> UnifiedAuditResult:
        query: Dict[str, Any] = {
            "api_key_id": api_key_id,
            "limit": limit,
            "event_types": ",".join(event_types) if event_types else None,
        }
        data = self._client.request("GET", "/audit", query=query)
        return UnifiedAuditResult.from_dict(data)


class AsyncAuditResource(AsyncBaseResource):
    async def list(
        self,
        *,
        api_key_id: str = "self",
        limit: Optional[int] = None,
        event_types: Optional[List[str]] = None,
    ) -> UnifiedAuditResult:
        query: Dict[str, Any] = {
            "api_key_id": api_key_id,
            "limit": limit,
            "event_types": ",".join(event_types) if event_types else None,
        }
        data = await self._client.request("GET", "/audit", query=query)
        return UnifiedAuditResult.from_dict(data)
