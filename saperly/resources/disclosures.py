from __future__ import annotations

from typing import Any, Dict, List, Optional

from .._types import Disclosure
from ._base import AsyncBaseResource, BaseResource


class DisclosuresResource(BaseResource):
    def create(
        self,
        *,
        message: str,
        audio_url: Optional[str] = None,
        language: Optional[str] = None,
        jurisdiction: Optional[str] = None,
    ) -> Disclosure:
        body: Dict[str, Any] = {"message": message}
        if audio_url is not None:
            body["audio_url"] = audio_url
        if language is not None:
            body["language"] = language
        if jurisdiction is not None:
            body["jurisdiction"] = jurisdiction
        data = self._client.request("POST", "/disclosures", body=body)
        return Disclosure.from_dict(data["disclosure"])

    def list(self) -> List[Disclosure]:
        data = self._client.request("GET", "/disclosures")
        return [Disclosure.from_dict(d) for d in data["disclosures"]]


class AsyncDisclosuresResource(AsyncBaseResource):
    async def create(
        self,
        *,
        message: str,
        audio_url: Optional[str] = None,
        language: Optional[str] = None,
        jurisdiction: Optional[str] = None,
    ) -> Disclosure:
        body: Dict[str, Any] = {"message": message}
        if audio_url is not None:
            body["audio_url"] = audio_url
        if language is not None:
            body["language"] = language
        if jurisdiction is not None:
            body["jurisdiction"] = jurisdiction
        data = await self._client.request("POST", "/disclosures", body=body)
        return Disclosure.from_dict(data["disclosure"])

    async def list(self) -> List[Disclosure]:
        data = await self._client.request("GET", "/disclosures")
        return [Disclosure.from_dict(d) for d in data["disclosures"]]
