from __future__ import annotations

from typing import Any, Dict, Optional

from .._types import AuditResult
from ._base import AsyncBaseResource, BaseResource


class ComplianceResource(BaseResource):
    def audit(
        self,
        *,
        line_id: Optional[str] = None,
        phone_number: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> AuditResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "phone_number": phone_number,
            "event_type": event_type,
            "from": from_date,
            "to": to_date,
            "limit": limit,
            "offset": offset,
        }
        data = self._client.request("GET", "/compliance/audit", query=query)
        return AuditResult.from_dict(data)


class AsyncComplianceResource(AsyncBaseResource):
    async def audit(
        self,
        *,
        line_id: Optional[str] = None,
        phone_number: Optional[str] = None,
        event_type: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> AuditResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "phone_number": phone_number,
            "event_type": event_type,
            "from": from_date,
            "to": to_date,
            "limit": limit,
            "offset": offset,
        }
        data = await self._client.request("GET", "/compliance/audit", query=query)
        return AuditResult.from_dict(data)
