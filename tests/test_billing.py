from __future__ import annotations

import responses

from saperly import Balance
from tests.conftest import BASE_URL


class TestBilling:
    def test_balance(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/billing/balance",
            json={"balance_cents": 500, "currency": "usd"},
            status=200,
        )
        balance = client.billing.balance()

        assert isinstance(balance, Balance)
        assert balance.balance_cents == 500
        assert balance.currency == "usd"
