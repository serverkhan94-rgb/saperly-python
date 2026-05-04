from __future__ import annotations

import pytest
import responses

from saperly import Balance, TransactionListResult
from tests.conftest import BASE_URL


class TestBilling:
    def test_balance(self, mock_api, client):
        # v0.5.3 cents-honest: server returns currency="USD" and `credits`
        # carries cents (500 = $5.00). The legacy "credits" currency string
        # is still accepted by the type for backward-compat with v0.5.1.x
        # snapshots, but new servers always emit "USD".
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/billing/balance",
            json={"credits": 500, "currency": "USD"},
            status=200,
        )
        balance = client.billing.balance()

        assert isinstance(balance, Balance)
        assert balance.credits == 500
        assert balance.currency == "USD"

    def test_add_funds_raises(self, client):
        # add_funds was removed in v0.5.2.0 (postpaid pivot). The Python SDK
        # raises synchronously with a migration breadcrumb instead of hitting
        # the deleted /billing/add-funds endpoint and surfacing an opaque 404.
        # Mirrors the TS SDK throw at packages/sdk/src/resources/billing.ts.
        with pytest.raises(RuntimeError, match="postpaid"):
            client.billing.add_funds(amount_credits=2500)

    def test_transactions(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/billing/transactions",
            json={
                "transactions": [
                    {
                        "id": "txn-1",
                        "type": "signup_credit",
                        "amount_credits": 500,
                        "balance_after_credits": 500,
                        "description": "Signup credit",
                        "reference_id": None,
                        "reference_type": None,
                        "created_at": "2026-01-01T00:00:00Z",
                    }
                ],
                "has_more": True,
                "next_cursor": "2026-01-01T00:00:00Z",
            },
            status=200,
        )
        result = client.billing.transactions(limit=10)

        assert isinstance(result, TransactionListResult)
        assert len(result.transactions) == 1
        assert result.transactions[0].amount_credits == 500
        assert result.transactions[0].type == "signup_credit"
        assert result.has_more is True
        assert result.next_cursor == "2026-01-01T00:00:00Z"

    def test_transactions_with_cursor(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/billing/transactions",
            json={"transactions": [], "has_more": False, "next_cursor": None},
            status=200,
        )
        result = client.billing.transactions(
            limit=5, cursor="2026-01-01T00:00:00Z"
        )

        assert result.has_more is False
        assert result.next_cursor is None
