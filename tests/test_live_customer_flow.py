"""v0.5.3 live-customer-flow E2E (Phase A.1d).

Mirrors the TS SDK A.1b structure: constructor → line create → call create →
message send → balance check, with sync (responses) and async (respx) variants.
Pins v0.5.3 signup grant flow-through and the canonical error envelope.

Notes on Python SDK shape vs TS SDK:
- Calls and messages use ``line_id`` / ``to_number`` / ``to`` / ``text`` —
  the Python SDK does not take ``from_`` / ``twiml`` / ``body``.
- Billing balance returns a ``Balance(credits=..., currency=...)`` dataclass,
  not a ``balance_cents`` field. The signup-grant assertion pins
  ``balance.credits == 500``.
- API code ``unauthorized`` maps to ``AuthenticationError`` whose constructor
  rewrites ``self.code`` to ``"invalid_api_key"``; we assert the subclass +
  status + message rather than the literal API code (matches SDK behavior).
"""

from __future__ import annotations

import httpx
import pytest
import responses
import respx

from saperly import (
    AsyncSaperlyClient,
    AuthenticationError,
    Balance,
    Call,
    Line,
    Message,
    SaperlyClient,
)

BASE_URL = "http://test"

LINE_FIXTURE = {
    "id": "line-live-1",
    "phone_number": "+14155550100",
    "display_name": None,
    "name": "live-flow",
    "mode": "webhook",
    "audio_handler_url": None,
    "webhook_url": "https://example.com/inbound",
    "status_callback_url": "https://example.com/status",
    "status": "active",
    "environment": "live",
    "created_at": "2026-05-03T00:00:00Z",
}

CALL_FIXTURE = {
    "id": "call-live-1",
    "line_id": "line-live-1",
    "direction": "outbound",
    "from_number": "+14155550100",
    "to_number": "+14155559999",
    "status": "initiated",
    "duration_sec": None,
    "started_at": None,
    "ended_at": None,
    "created_at": "2026-05-03T00:00:00Z",
}

MESSAGE_FIXTURE = {
    "id": "msg-live-1",
    "line_id": "line-live-1",
    "to": "+14155559999",
    "text": "Welcome aboard",
    "status": "sent",
    "created_at": "2026-05-03T00:00:00Z",
}


class TestLiveCustomerFlowSync:
    def test_constructor_sets_bearer_auth(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/api/v1/lines",
                json={"lines": [LINE_FIXTURE]},
                status=200,
            )
            client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
            client.lines.list()

            assert (
                rsps.calls[0].request.headers["Authorization"] == "Bearer sk_test_xyz"
            )

    def test_lines_create_returns_line_with_phone_number(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{BASE_URL}/api/v1/lines",
                json={"line": LINE_FIXTURE},
                status=201,
            )
            client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
            line = client.lines.create(
                name="live-flow",
                mode="webhook",
                webhook_url="https://example.com/inbound",
                status_callback_url="https://example.com/status",
            )

            assert isinstance(line, Line)
            assert line.id == "line-live-1"
            assert line.phone_number == "+14155550100"
            assert line.mode == "webhook"
            assert line.webhook_url == "https://example.com/inbound"

    def test_calls_create_returns_initiated_call(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{BASE_URL}/api/v1/calls",
                json={"call": CALL_FIXTURE},
                status=201,
            )
            client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
            call = client.calls.create(
                line_id="line-live-1",
                to_number="+14155559999",
            )

            assert isinstance(call, Call)
            assert call.status == "initiated"
            assert call.line_id == "line-live-1"
            # cost_cents is intentionally absent from the SDK shape (mirrors TS SDK)
            assert not hasattr(call, "cost_cents")

    def test_messages_send_returns_message_with_status(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                f"{BASE_URL}/api/v1/messages",
                json=MESSAGE_FIXTURE,
                status=201,
            )
            client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
            msg = client.messages.send(
                line_id="line-live-1",
                to="+14155559999",
                text="Welcome aboard",
            )

            assert isinstance(msg, Message)
            assert msg.id == "msg-live-1"
            assert msg.status == "sent"
            assert not hasattr(msg, "cost_cents")

    def test_lines_list_returns_multiple(self):
        second = {**LINE_FIXTURE, "id": "line-live-2", "phone_number": "+14155550101"}
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/api/v1/lines",
                json={"lines": [LINE_FIXTURE, second]},
                status=200,
            )
            client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
            lines = client.lines.list()

            assert len(lines) == 2
            assert [ln.id for ln in lines] == ["line-live-1", "line-live-2"]

    def test_unauthorized_envelope_raises_authentication_error(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/api/v1/lines",
                json={
                    "error": {
                        "code": "unauthorized",
                        "message": "API key revoked",
                        "details": [],
                    }
                },
                status=401,
            )
            client = SaperlyClient(api_key="sk_revoked", base_url=BASE_URL)

            with pytest.raises(AuthenticationError) as exc_info:
                client.lines.list()

            # NOTE: AuthenticationError.__init__ rewrites code → "invalid_api_key";
            # we pin status + message to verify envelope flow-through.
            assert exc_info.value.status == 401
            assert str(exc_info.value) == "API key revoked"

    def test_billing_balance_pins_v053_signup_grant(self):
        # v0.5.3 cents-honest pivot: server returns currency="USD". The legacy
        # "credits" currency would also pass a credits==500 assertion alone, so
        # we pin the currency literal too — that's the actual v0.5.3 contract
        # change (see src/app/api/v1/billing/balance/route.ts).
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/api/v1/billing/balance",
                json={"credits": 500, "currency": "USD"},
                status=200,
            )
            client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
            balance = client.billing.balance()

            assert isinstance(balance, Balance)
            assert balance.credits == 500
            assert balance.currency == "USD"


class TestLiveCustomerFlowAsync:
    # Relies on asyncio_mode = "auto" in pyproject.toml (line 33). If that
    # config is ever flipped to "strict", these tests would be silently
    # SKIPPED rather than failing — add explicit @pytest.mark.asyncio
    # decorators if the project moves to strict mode.

    @respx.mock
    async def test_lines_create_returns_line(self):
        respx.post(f"{BASE_URL}/api/v1/lines").mock(
            return_value=httpx.Response(201, json={"line": LINE_FIXTURE}),
        )
        client = AsyncSaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
        line = await client.lines.create(
            name="live-flow",
            mode="webhook",
            webhook_url="https://example.com/inbound",
            status_callback_url="https://example.com/status",
        )

        assert isinstance(line, Line)
        assert line.phone_number == "+14155550100"
        assert line.mode == "webhook"
        await client.aclose()

    @respx.mock
    async def test_calls_create_returns_initiated_call(self):
        respx.post(f"{BASE_URL}/api/v1/calls").mock(
            return_value=httpx.Response(201, json={"call": CALL_FIXTURE}),
        )
        client = AsyncSaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
        call = await client.calls.create(
            line_id="line-live-1",
            to_number="+14155559999",
        )

        assert isinstance(call, Call)
        assert call.status == "initiated"
        await client.aclose()

    @respx.mock
    async def test_messages_send_returns_message(self):
        respx.post(f"{BASE_URL}/api/v1/messages").mock(
            return_value=httpx.Response(201, json=MESSAGE_FIXTURE),
        )
        client = AsyncSaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
        msg = await client.messages.send(
            line_id="line-live-1",
            to="+14155559999",
            text="Welcome aboard",
        )

        assert isinstance(msg, Message)
        assert msg.status == "sent"
        await client.aclose()

    @respx.mock
    async def test_billing_balance_pins_v053_signup_grant_async(self):
        # Coverage symmetry with the sync test: pin v0.5.3 cents-honest pivot
        # (currency: "USD") so a regression to the legacy "credits" currency
        # fails the test rather than silently passing on credits == 500.
        respx.get(f"{BASE_URL}/api/v1/billing/balance").mock(
            return_value=httpx.Response(200, json={"credits": 500, "currency": "USD"}),
        )
        client = AsyncSaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
        balance = await client.billing.balance()

        assert isinstance(balance, Balance)
        assert balance.credits == 500
        assert balance.currency == "USD"
        await client.aclose()

    @respx.mock
    async def test_unauthorized_envelope_raises_authentication_error_async(self):
        respx.get(f"{BASE_URL}/api/v1/lines").mock(
            return_value=httpx.Response(
                401,
                json={
                    "error": {
                        "code": "unauthorized",
                        "message": "API key revoked",
                        "details": [],
                    },
                },
            ),
        )
        client = AsyncSaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)

        with pytest.raises(AuthenticationError) as exc_info:
            await client.lines.list()

        # AuthenticationError.__init__ rewrites code → "invalid_api_key";
        # pin status + message instead to verify envelope flow-through.
        assert exc_info.value.status == 401
        assert str(exc_info.value) == "API key revoked"
        await client.aclose()

    @respx.mock
    async def test_async_constructor_sets_bearer_auth(self):
        captured_headers: dict[str, str] = {}

        def capture(request):
            captured_headers.update(request.headers)
            return httpx.Response(200, json={"lines": []})

        respx.get(f"{BASE_URL}/api/v1/lines").mock(side_effect=capture)
        client = AsyncSaperlyClient(api_key="sk_test_async", base_url=BASE_URL)
        await client.lines.list()
        await client.aclose()

        assert captured_headers.get("authorization") == "Bearer sk_test_async"
