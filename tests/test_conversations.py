from __future__ import annotations

import responses

from saperly import ConversationListResult, ConversationMessagesResult
from tests.conftest import BASE_URL, SAMPLE_CONVERSATION


class TestConversations:
    def test_list_returns_result(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/conversations",
            json={
                "conversations": [SAMPLE_CONVERSATION],
                "has_more": False,
                "next_cursor": None,
            },
            status=200,
        )
        result = client.conversations.list()

        assert isinstance(result, ConversationListResult)
        assert len(result.conversations) == 1
        assert result.conversations[0].line_id == "line_1"
        assert result.conversations[0].phone_number == "+15551234567"
        assert result.conversations[0].message_count == 5
        assert result.has_more is False

    def test_list_passes_query_params(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/conversations",
            json={"conversations": [], "has_more": False, "next_cursor": None},
            status=200,
        )
        client.conversations.list(line_id="line_1", limit=10, cursor="abc")

        request_url = mock_api.calls[0].request.url
        assert "line_id=line_1" in request_url
        assert "limit=10" in request_url
        assert "cursor=abc" in request_url

    def test_messages_returns_result(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/conversations/line_1/%2B15551234567",
            json={
                "messages": [
                    {"direction": "inbound", "text": "Hi", "timestamp": "2026-01-01T00:00:00Z"},
                ],
                "has_more": False,
                "next_cursor": None,
            },
            status=200,
        )
        result = client.conversations.messages("line_1", "+15551234567")

        assert isinstance(result, ConversationMessagesResult)
        assert len(result.messages) == 1
        assert result.messages[0].direction == "inbound"
        assert result.messages[0].text == "Hi"
        assert result.has_more is False
