from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List, Optional

from .._types import Line, SmsMessage
from ._base import AsyncBaseResource, BaseResource


class LinesResource(BaseResource):
    def create(
        self,
        *,
        name: str,
        mode: str = "audio",
        webhook_url: Optional[str] = None,
        audio_handler_url: Optional[str] = None,
        status_callback_url: Optional[str] = None,
    ) -> Line:
        body: Dict[str, Any] = {"name": name, "mode": mode}
        if webhook_url is not None:
            body["webhook_url"] = webhook_url
        if audio_handler_url is not None:
            body["audio_handler_url"] = audio_handler_url
        if status_callback_url is not None:
            body["status_callback_url"] = status_callback_url
        data = self._client.request("POST", "/lines", body=body)
        return Line.from_dict(data["line"])

    def list(self) -> List[Line]:
        data = self._client.request("GET", "/lines")
        return [Line.from_dict(item) for item in data["lines"]]

    def get(self, line_id: str) -> Line:
        encoded = urllib.parse.quote(line_id, safe="")
        data = self._client.request("GET", f"/lines/{encoded}")
        return Line.from_dict(data["line"])

    def delete(self, line_id: str) -> Line:
        encoded = urllib.parse.quote(line_id, safe="")
        data = self._client.request("DELETE", f"/lines/{encoded}")
        return Line.from_dict(data["line"])

    def send_sms(self, line_id: str, *, to_number: str, message: str) -> SmsMessage:
        encoded = urllib.parse.quote(line_id, safe="")
        body = {"to_number": to_number, "message": message}
        data = self._client.request("POST", f"/lines/{encoded}/sms", body=body)
        return SmsMessage.from_dict(data["sms"])


class AsyncLinesResource(AsyncBaseResource):
    async def create(
        self,
        *,
        name: str,
        mode: str = "audio",
        webhook_url: Optional[str] = None,
        audio_handler_url: Optional[str] = None,
        status_callback_url: Optional[str] = None,
    ) -> Line:
        body: Dict[str, Any] = {"name": name, "mode": mode}
        if webhook_url is not None:
            body["webhook_url"] = webhook_url
        if audio_handler_url is not None:
            body["audio_handler_url"] = audio_handler_url
        if status_callback_url is not None:
            body["status_callback_url"] = status_callback_url
        data = await self._client.request("POST", "/lines", body=body)
        return Line.from_dict(data["line"])

    async def list(self) -> List[Line]:
        data = await self._client.request("GET", "/lines")
        return [Line.from_dict(item) for item in data["lines"]]

    async def get(self, line_id: str) -> Line:
        encoded = urllib.parse.quote(line_id, safe="")
        data = await self._client.request("GET", f"/lines/{encoded}")
        return Line.from_dict(data["line"])

    async def delete(self, line_id: str) -> Line:
        encoded = urllib.parse.quote(line_id, safe="")
        data = await self._client.request("DELETE", f"/lines/{encoded}")
        return Line.from_dict(data["line"])

    async def send_sms(self, line_id: str, *, to_number: str, message: str) -> SmsMessage:
        encoded = urllib.parse.quote(line_id, safe="")
        body = {"to_number": to_number, "message": message}
        data = await self._client.request("POST", f"/lines/{encoded}/sms", body=body)
        return SmsMessage.from_dict(data["sms"])
