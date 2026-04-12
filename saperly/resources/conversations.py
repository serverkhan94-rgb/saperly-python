from __future__ import annotations

import urllib.parse
from typing import Any, Dict, Optional

from .._types import ConversationListResult, ConversationMessagesResult
from ._base import AsyncBaseResource, BaseResource


class ConversationsResource(BaseResource):
    def list(
        self,
        *,
        line_id: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ConversationListResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "limit": limit,
            "cursor": cursor,
        }
        data = self._client.request("GET", "/conversations", query=query)
        return ConversationListResult.from_dict(data)

    def messages(
        self,
        line_id: str,
        phone_number: str,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ConversationMessagesResult:
        encoded_line = urllib.parse.quote(line_id, safe="")
        encoded_phone = urllib.parse.quote(phone_number, safe="")
        query: Dict[str, Any] = {"limit": limit, "cursor": cursor}
        data = self._client.request(
            "GET",
            f"/conversations/{encoded_line}/{encoded_phone}",
            query=query,
        )
        return ConversationMessagesResult.from_dict(data)


class AsyncConversationsResource(AsyncBaseResource):
    async def list(
        self,
        *,
        line_id: Optional[str] = None,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ConversationListResult:
        query: Dict[str, Any] = {
            "line_id": line_id,
            "limit": limit,
            "cursor": cursor,
        }
        data = await self._client.request("GET", "/conversations", query=query)
        return ConversationListResult.from_dict(data)

    async def messages(
        self,
        line_id: str,
        phone_number: str,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> ConversationMessagesResult:
        encoded_line = urllib.parse.quote(line_id, safe="")
        encoded_phone = urllib.parse.quote(phone_number, safe="")
        query: Dict[str, Any] = {"limit": limit, "cursor": cursor}
        data = await self._client.request(
            "GET",
            f"/conversations/{encoded_line}/{encoded_phone}",
            query=query,
        )
        return ConversationMessagesResult.from_dict(data)
