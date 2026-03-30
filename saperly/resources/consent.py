from __future__ import annotations

from typing import Any, Dict, Optional

from .._types import ConsentCheckResult, ConsentRecord
from ._base import AsyncBaseResource, BaseResource


class ConsentResource(BaseResource):
    def grant(
        self,
        *,
        line_id: str,
        phone_number: str,
        consent_type: str,
        source: str,
    ) -> ConsentRecord:
        body = {
            "line_id": line_id,
            "phone_number": phone_number,
            "consent_type": consent_type,
            "source": source,
        }
        data = self._client.request("POST", "/consent", body=body)
        return ConsentRecord.from_dict(data["consent"])

    def check(
        self,
        *,
        phone_number: str,
        line_id: Optional[str] = None,
    ) -> ConsentCheckResult:
        query: Dict[str, Any] = {
            "phone_number": phone_number,
            "line_id": line_id,
        }
        data = self._client.request("GET", "/consent", query=query)
        return ConsentCheckResult.from_dict(data)

    def revoke(
        self,
        *,
        phone_number: str,
        line_id: Optional[str] = None,
    ) -> ConsentRecord:
        query: Dict[str, Any] = {
            "phone_number": phone_number,
            "line_id": line_id,
        }
        data = self._client.request("DELETE", "/consent", query=query)
        return ConsentRecord.from_dict(data["consent"])


class AsyncConsentResource(AsyncBaseResource):
    async def grant(
        self,
        *,
        line_id: str,
        phone_number: str,
        consent_type: str,
        source: str,
    ) -> ConsentRecord:
        body = {
            "line_id": line_id,
            "phone_number": phone_number,
            "consent_type": consent_type,
            "source": source,
        }
        data = await self._client.request("POST", "/consent", body=body)
        return ConsentRecord.from_dict(data["consent"])

    async def check(
        self,
        *,
        phone_number: str,
        line_id: Optional[str] = None,
    ) -> ConsentCheckResult:
        query: Dict[str, Any] = {
            "phone_number": phone_number,
            "line_id": line_id,
        }
        data = await self._client.request("GET", "/consent", query=query)
        return ConsentCheckResult.from_dict(data)

    async def revoke(
        self,
        *,
        phone_number: str,
        line_id: Optional[str] = None,
    ) -> ConsentRecord:
        query: Dict[str, Any] = {
            "phone_number": phone_number,
            "line_id": line_id,
        }
        data = await self._client.request("DELETE", "/consent", query=query)
        return ConsentRecord.from_dict(data["consent"])
