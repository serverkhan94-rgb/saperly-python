from __future__ import annotations

from typing import Any, Dict

from .._types import Message
from ._base import AsyncBaseResource, BaseResource


class MessagesResource(BaseResource):
    def send(self, *, line_id: str, to: str, text: str) -> Message:
        body: Dict[str, Any] = {"line_id": line_id, "to": to, "text": text}
        data = self._client.request("POST", "/messages", body=body)
        return Message.from_dict(data)


class AsyncMessagesResource(AsyncBaseResource):
    async def send(self, *, line_id: str, to: str, text: str) -> Message:
        body: Dict[str, Any] = {"line_id": line_id, "to": to, "text": text}
        data = await self._client.request("POST", "/messages", body=body)
        return Message.from_dict(data)
