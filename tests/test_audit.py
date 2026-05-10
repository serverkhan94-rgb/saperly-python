from __future__ import annotations

import httpx
import pytest
import responses
import respx

from saperly import (
    AgentScopeError,
    AsyncSaperlyClient,
    AuditResult,
    SaperlyClient,
    UnifiedAuditEvent,
    UnifiedAuditResult,
)
from tests.conftest import BASE_URL, SAMPLE_EVENT

SAMPLE_AUDIT_PAYLOAD = {
    "events": [
        {
            "type": "call",
            "id": "call-1",
            "created_at": "2026-05-09T12:00:00.000Z",
            "data": {
                "direction": "outbound",
                "from_number": "+14155550123",
                "to_number": "+14155559999",
                "status": "completed",
                "duration_sec": 42,
                "started_at": "2026-05-09T11:59:00.000Z",
                "ended_at": "2026-05-09T11:59:42.000Z",
                "line_id": "line-1",
            },
        },
        {
            "type": "sms",
            "id": "sms-1",
            "created_at": "2026-05-09T11:50:00.000Z",
            "data": {
                "from_number": "+14155550123",
                "to_number": "+14155559999",
                "status": "delivered",
                "segments": 1,
                "destination_zone": "A",
                "line_id": "line-1",
            },
        },
        {
            "type": "compliance_event",
            "id": "ce-1",
            "created_at": "2026-05-09T11:40:00.000Z",
            "data": {
                "event_type": "call_started",
                "line_id": "line-1",
                "call_id": "call-1",
                "phone_number": "+14155559999",
                "metadata": {"source": "outbound"},
            },
        },
        {
            "type": "billing_transaction",
            "id": "bt-1",
            "created_at": "2026-05-09T11:30:00.000Z",
            "data": {
                "transaction_type": "charge",
                "amount_cents": -13,
                "balance_after_cents": 487,
                "description": "voice 1 min",
                "status": "completed",
                "reference_id": "call-1",
                "reference_type": "call",
            },
        },
    ],
    "limit": 100,
    "api_key_id": "key-uuid-1",
}


class TestAuditSync:
    def test_list_happy_path(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/audit",
            json=SAMPLE_AUDIT_PAYLOAD,
            status=200,
        )
        result = client.audit.list()

        assert isinstance(result, UnifiedAuditResult)
        assert result.limit == 100
        assert result.api_key_id == "key-uuid-1"
        assert len(result.events) == 4
        for event in result.events:
            assert isinstance(event, UnifiedAuditEvent)
        # Discriminator + per-type data preserved as snake_case dict
        call_event = result.events[0]
        assert call_event.type == "call"
        assert call_event.id == "call-1"
        assert call_event.created_at == "2026-05-09T12:00:00.000Z"
        assert call_event.data["from_number"] == "+14155550123"
        assert call_event.data["duration_sec"] == 42
        sms_event = result.events[1]
        assert sms_event.type == "sms"
        assert sms_event.data["destination_zone"] == "A"
        ce_event = result.events[2]
        assert ce_event.type == "compliance_event"
        assert ce_event.data["event_type"] == "call_started"
        bt_event = result.events[3]
        assert bt_event.type == "billing_transaction"
        assert bt_event.data["amount_cents"] == -13
        assert bt_event.data["reference_type"] == "call"

    def test_list_defaults_api_key_id_to_self(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/audit",
            json={"events": [], "limit": 100, "api_key_id": "key-self"},
            status=200,
        )
        client.audit.list()

        request_url = mock_api.calls[0].request.url
        assert "api_key_id=self" in request_url

    def test_list_serializes_limit_and_event_types_csv(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/audit",
            json={"events": [], "limit": 50, "api_key_id": "key-self"},
            status=200,
        )
        client.audit.list(limit=50, event_types=["call", "sms"])

        request_url = mock_api.calls[0].request.url
        assert "limit=50" in request_url
        # CSV serialization; comma may be URL-encoded as %2C
        assert "event_types=call%2Csms" in request_url or "event_types=call,sms" in request_url

    def test_list_propagates_typed_error(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/audit",
            json={
                "error": {
                    "code": "agent_scope_error",
                    "message": "Line-scoped key cannot read another key's audit.",
                    "details": [
                        {"field": "line_id", "message": "/v1/audit"},
                    ],
                },
            },
            status=403,
        )
        with pytest.raises(AgentScopeError) as excinfo:
            client.audit.list(api_key_id="key-other")
        err = excinfo.value
        assert err.code == "agent_scope_error"
        assert err.status == 403
        assert len(err.details) == 1
        assert err.details[0].field == "line_id"

    def test_backwards_compat_compliance_audit_still_returns_legacy(
        self, mock_api, client
    ):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/compliance/audit",
            json={"events": [SAMPLE_EVENT], "total": 1},
            status=200,
        )
        result = client.compliance.audit()

        assert isinstance(result, AuditResult)
        # Legacy AuditResult shape — has `total`, NOT `limit`/`api_key_id`
        assert result.total == 1
        assert len(result.events) == 1
        # Legacy events are ComplianceEvent dataclass, not UnifiedAuditEvent
        legacy_event = result.events[0]
        assert not isinstance(legacy_event, UnifiedAuditEvent)
        assert legacy_event.event_type == "call_started"


class TestAuditAsync:
    @respx.mock
    async def test_list_happy_path(self):
        respx.get(f"{BASE_URL}/api/v1/audit").mock(
            return_value=httpx.Response(200, json=SAMPLE_AUDIT_PAYLOAD),
        )
        client = AsyncSaperlyClient(api_key="sk_test_async", base_url=BASE_URL)
        result = await client.audit.list()

        assert isinstance(result, UnifiedAuditResult)
        assert result.limit == 100
        assert result.api_key_id == "key-uuid-1"
        assert len(result.events) == 4
        assert result.events[0].type == "call"
        assert result.events[0].data["from_number"] == "+14155550123"
        await client.aclose()


class TestAuditClientWiring:
    def test_sync_client_has_audit_attribute(self):
        c = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        assert hasattr(c, "audit")
        assert c.audit is not None
        c.close()

    def test_async_client_has_audit_attribute(self):
        c = AsyncSaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        assert hasattr(c, "audit")
        assert c.audit is not None
