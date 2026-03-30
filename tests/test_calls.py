from __future__ import annotations

import responses

from saperly import Call
from tests.conftest import BASE_URL, SAMPLE_CALL


class TestCalls:
    def test_create_returns_call(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/calls",
            json={"call": SAMPLE_CALL},
            status=201,
        )
        call = client.calls.create(line_id="line-1", to_number="+14155559999")

        assert isinstance(call, Call)
        assert call.id == "call-1"
        assert call.line_id == "line-1"
        assert call.direction == "outbound"
        assert call.status == "initiated"

    def test_list_passes_query_params(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/calls",
            json={"calls": [SAMPLE_CALL], "total": 1},
            status=200,
        )
        result = client.calls.list(line_id="line-1", status="initiated", limit=10)

        request_url = mock_api.calls[0].request.url
        assert "line_id=line-1" in request_url
        assert "status=initiated" in request_url
        assert "limit=10" in request_url
        assert result.total == 1
        assert len(result.calls) == 1

    def test_hangup(self, mock_api, client):
        completed_call = {**SAMPLE_CALL, "status": "completed"}
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/calls/call-1/hangup",
            json={"call": completed_call},
            status=200,
        )
        call = client.calls.hangup("call-1")

        assert isinstance(call, Call)
        assert call.status == "completed"
