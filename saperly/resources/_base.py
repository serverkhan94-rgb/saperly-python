from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._client import AsyncSaperlyClient, SaperlyClient


class BaseResource:
    def __init__(self, client: SaperlyClient) -> None:
        self._client = client


class AsyncBaseResource:
    def __init__(self, client: AsyncSaperlyClient) -> None:
        self._client = client
