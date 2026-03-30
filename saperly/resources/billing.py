from __future__ import annotations

from .._types import Balance
from ._base import AsyncBaseResource, BaseResource


class BillingResource(BaseResource):
    def balance(self) -> Balance:
        data = self._client.request("GET", "/billing/balance")
        return Balance.from_dict(data)


class AsyncBillingResource(AsyncBaseResource):
    async def balance(self) -> Balance:
        data = await self._client.request("GET", "/billing/balance")
        return Balance.from_dict(data)
