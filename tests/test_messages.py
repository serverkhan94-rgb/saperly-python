from __future__ import annotations

import responses

from saperly import Message
from tests.conftest import BASE_URL, SAMPLE_MESSAGE


class TestMessages:
    def test_send_returns_message(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/messages",
            json=SAMPLE_MESSAGE,
            status=201,
        )
        msg = client.messages.send(line_id="line_1", to="+15551234567", text="Hello")

        assert isinstance(msg, Message)
        assert msg.id == "msg_1"
        assert msg.line_id == "line_1"
        assert msg.to == "+15551234567"
        assert msg.text == "Hello"
        assert msg.status == "sent"

    def test_send_passes_correct_body(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/messages",
            json=SAMPLE_MESSAGE,
            status=201,
        )
        client.messages.send(line_id="line_1", to="+15551234567", text="Hello")

        body = mock_api.calls[0].request.body
        assert b'"line_id"' in body
        assert b'"to"' in body
        assert b'"text"' in body
