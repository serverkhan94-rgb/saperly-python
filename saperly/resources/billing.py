from __future__ import annotations

from typing import Any, Dict, Optional

from .._types import AddFundsResult, Balance, TransactionListResult
from ._base import AsyncBaseResource, BaseResource


class BillingResource(BaseResource):
    def balance(self) -> Balance:
        data = self._client.request("GET", "/billing/balance")
        return Balance.from_dict(data)

    def add_funds(self, *, amount_cents: int) -> AddFundsResult:
        body = {"amount_cents": amount_cents}
        data = self._client.request("POST", "/billing/add-funds", body=body)
        return AddFundsResult.from_dict(data)

    def transactions(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TransactionListResult:
        query: Dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if cursor is not None:
            query["cursor"] = cursor
        data = self._client.request("GET", "/billing/transactions", query=query)
        return TransactionListResult.from_dict(data)


class AsyncBillingResource(AsyncBaseResource):
    async def balance(self) -> Balance:
        data = await self._client.request("GET", "/billing/balance")
        return Balance.from_dict(data)

    async def add_funds(self, *, amount_cents: int) -> AddFundsResult:
        body = {"amount_cents": amount_cents}
        data = await self._client.request("POST", "/billing/add-funds", body=body)
        return AddFundsResult.from_dict(data)

    async def transactions(
        self,
        *,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> TransactionListResult:
        query: Dict[str, Any] = {}
        if limit is not None:
            query["limit"] = limit
        if cursor is not None:
            query["cursor"] = cursor
        data = await self._client.request("GET", "/billing/transactions", query=query)
        return TransactionListResult.from_dict(data)
