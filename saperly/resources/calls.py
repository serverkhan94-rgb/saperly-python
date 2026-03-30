from __future__ import annotations

import urllib.parse
from typing import Any, Dict, Optional

from .._types import Call, CallListResult
from ._base import AsyncBaseResource, BaseResource


class CallsResource(BaseResource):
    def create(self, *, line_id: str, to_number: str) -> Call:
        body = {"line_id": line_id, "to_number": to_number}
        data = self._client.request("POST", "/calls", body=body)
        return Call.from_dict(data["call"])

    def list(
        self,
        *,
        line_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> CallListResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        data = self._client.request("GET", "/calls", query=query)
        return CallListResult.from_dict(data)

    def get(self, call_id: str) -> Call:
        encoded = urllib.parse.quote(call_id, safe="")
        data = self._client.request("GET", f"/calls/{encoded}")
        return Call.from_dict(data["call"])

    def hangup(self, call_id: str) -> Call:
        encoded = urllib.parse.quote(call_id, safe="")
        data = self._client.request("POST", f"/calls/{encoded}/hangup")
        return Call.from_dict(data["call"])


class AsyncCallsResource(AsyncBaseResource):
    async def create(self, *, line_id: str, to_number: str) -> Call:
        body = {"line_id": line_id, "to_number": to_number}
        data = await self._client.request("POST", "/calls", body=body)
        return Call.from_dict(data["call"])

    async def list(
        self,
        *,
        line_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> CallListResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "status": status,
            "limit": limit,
            "offset": offset,
        }
        data = await self._client.request("GET", "/calls", query=query)
        return CallListResult.from_dict(data)

    async def get(self, call_id: str) -> Call:
        encoded = urllib.parse.quote(call_id, safe="")
        data = await self._client.request("GET", f"/calls/{encoded}")
        return Call.from_dict(data["call"])

    async def hangup(self, call_id: str) -> Call:
        encoded = urllib.parse.quote(call_id, safe="")
        data = await self._client.request("POST", f"/calls/{encoded}/hangup")
        return Call.from_dict(data["call"])
