from __future__ import annotations

from typing import Any, Dict, Optional

from .._types import AddFundsResult, Balance, TransactionListResult
from ._base import AsyncBaseResource, BaseResource


_ADD_FUNDS_DEPRECATION_MSG = (
    "client.billing.add_funds() was removed in v0.5.2.0. Saperly is now "
    "postpaid — your saved card on file is auto-charged when balance runs "
    "low. Manage payment methods at https://app.saperly.com/billing"
)


class BillingResource(BaseResource):
    def balance(self) -> Balance:
        data = self._client.request("GET", "/billing/balance")
        return Balance.from_dict(data)

    def add_funds(self, *, amount_credits: int) -> AddFundsResult:
        """
        Removed in v0.5.2.0. Saperly is now postpaid — your saved card on file
        is auto-charged when balance runs low. Manage payment methods at
        https://app.saperly.com/billing

        The signature is preserved for backward type-compat; calling it raises
        synchronously so v0.5.1.x consumers fail fast instead of hitting a
        404 on the deleted endpoint. Mirrors the TypeScript SDK pattern in
        packages/sdk/src/resources/billing.ts.
        """
        del amount_credits
        raise RuntimeError(_ADD_FUNDS_DEPRECATION_MSG)

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

    async def add_funds(self, *, amount_credits: int) -> AddFundsResult:
        """
        Removed in v0.5.2.0. See BillingResource.add_funds for migration
        details. Raises synchronously (no await needed for the failure).
        """
        del amount_credits
        raise RuntimeError(_ADD_FUNDS_DEPRECATION_MSG)

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
