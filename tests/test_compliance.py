from __future__ import annotations

import responses

from saperly import AuditResult, ComplianceEvent
from tests.conftest import BASE_URL, SAMPLE_EVENT


class TestCompliance:
    def test_audit_returns_events(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/compliance/audit",
            json={"events": [SAMPLE_EVENT], "total": 1},
            status=200,
        )
        result = client.compliance.audit()

        assert isinstance(result, AuditResult)
        assert result.total == 1
        assert len(result.events) == 1
        assert isinstance(result.events[0], ComplianceEvent)
        assert result.events[0].id == "event-1"
        assert result.events[0].event_type == "call_started"
        assert result.events[0].metadata == {"source": "outbound"}
