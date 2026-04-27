from __future__ import annotations

import responses

from saperly import AddFundsResult, Balance, TransactionListResult
from tests.conftest import BASE_URL


class TestBilling:
    def test_balance(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/billing/balance",
            json={"credits": 500, "currency": "credits"},
            status=200,
        )
        balance = client.billing.balance()

        assert isinstance(balance, Balance)
        assert balance.credits == 500
        assert balance.currency == "credits"

    def test_add_funds(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/billing/add-funds",
            json={"checkout_url": "https://checkout.stripe.com/pay/abc123"},
            status=201,
        )
        result = client.billing.add_funds(amount_credits=2500)

        assert isinstance(result, AddFundsResult)
        assert result.checkout_url == "https://checkout.stripe.com/pay/abc123"

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
