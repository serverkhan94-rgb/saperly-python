from __future__ import annotations

from typing import Any, Dict, Optional

from .._types import DailyUsageResult, MonthlyUsageResult
from ._base import AsyncBaseResource, BaseResource


class UsageResource(BaseResource):
    def daily(self, *, days: Optional[int] = None) -> DailyUsageResult:
        query: Dict[str, Any] = {"days": days}
        data = self._client.request("GET", "/usage/daily", query=query)
        return DailyUsageResult.from_dict(data)

    def monthly(self, *, months: Optional[int] = None) -> MonthlyUsageResult:
        query: Dict[str, Any] = {"months": months}
        data = self._client.request("GET", "/usage/monthly", query=query)
        return MonthlyUsageResult.from_dict(data)


class AsyncUsageResource(AsyncBaseResource):
    async def daily(self, *, days: Optional[int] = None) -> DailyUsageResult:
        query: Dict[str, Any] = {"days": days}
        data = await self._client.request("GET", "/usage/daily", query=query)
        return DailyUsageResult.from_dict(data)

    async def monthly(self, *, months: Optional[int] = None) -> MonthlyUsageResult:
        query: Dict[str, Any] = {"months": months}
        data = await self._client.request("GET", "/usage/monthly", query=query)
        return MonthlyUsageResult.from_dict(data)
