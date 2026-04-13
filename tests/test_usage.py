from __future__ import annotations

import responses

from saperly import DailyUsageResult, MonthlyUsageResult
from tests.conftest import BASE_URL, SAMPLE_DAILY_USAGE, SAMPLE_MONTHLY_USAGE


class TestUsage:
    def test_daily_returns_result(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/usage/daily",
            json={"daily": [SAMPLE_DAILY_USAGE]},
            status=200,
        )
        result = client.usage.daily()

        assert isinstance(result, DailyUsageResult)
        assert len(result.daily) == 1
        assert result.daily[0].date == "2026-01-01"
        assert result.daily[0].calls == 10
        assert result.daily[0].minutes == 45
        assert result.daily[0].sms_inbound == 3
        assert result.daily[0].cost_credits == 495

    def test_daily_passes_days_param(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/usage/daily",
            json={"daily": []},
            status=200,
        )
        client.usage.daily(days=7)

        request_url = mock_api.calls[0].request.url
        assert "days=7" in request_url

    def test_monthly_returns_result(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/usage/monthly",
            json={"monthly": [SAMPLE_MONTHLY_USAGE]},
            status=200,
        )
        result = client.usage.monthly()

        assert isinstance(result, MonthlyUsageResult)
        assert len(result.monthly) == 1
        assert result.monthly[0].month == "2026-01"
        assert result.monthly[0].calls == 100
        assert result.monthly[0].minutes == 450
        assert result.monthly[0].cost_credits == 4950

    def test_monthly_passes_months_param(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/usage/monthly",
            json={"monthly": []},
            status=200,
        )
        client.usage.monthly(months=3)

        request_url = mock_api.calls[0].request.url
        assert "months=3" in request_url
