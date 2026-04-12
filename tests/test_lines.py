from __future__ import annotations

import responses

from saperly import Line, SmsMessage
from tests.conftest import BASE_URL, SAMPLE_LINE


class TestLines:
    def test_create_returns_line(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/lines",
            json={"line": SAMPLE_LINE},
            status=201,
        )
        line = client.lines.create(name="support", mode="text")

        assert isinstance(line, Line)
        assert line.id == "line-1"
        assert line.phone_number == "+14155550123"
        assert line.name == "support"
        assert line.mode == "text"
        assert line.status == "active"
        assert line.webhook_url == "https://example.com/hook"

    def test_list_returns_lines(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/lines",
            json={"lines": [SAMPLE_LINE]},
            status=200,
        )
        lines = client.lines.list()

        assert len(lines) == 1
        assert isinstance(lines[0], Line)
        assert lines[0].id == "line-1"

    def test_delete_returns_released(self, mock_api, client):
        released = {**SAMPLE_LINE, "status": "released"}
        mock_api.add(
            responses.DELETE,
            f"{BASE_URL}/api/v1/lines/line-1",
            json={"line": released},
            status=200,
        )
        line = client.lines.delete("line-1")

        assert isinstance(line, Line)
        assert line.status == "released"

    def test_send_sms(self, mock_api, client):
        sms_response = {
            "id": "sms-1",
            "from_number": "+14155550123",
            "to_number": "+14155559999",
            "message": "Hello from AI",
            "status": "sent",
            "created_at": "2026-01-01T00:00:00Z",
        }
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/lines/line-1/sms",
            json={"sms": sms_response},
            status=200,
        )
        sms = client.lines.send_sms("line-1", to_number="+14155559999", message="Hello from AI")

        assert isinstance(sms, SmsMessage)
        assert sms.id == "sms-1"
        assert sms.to_number == "+14155559999"
        assert sms.message == "Hello from AI"
