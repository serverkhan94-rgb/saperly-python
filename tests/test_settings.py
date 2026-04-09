from __future__ import annotations

import responses

from saperly import Settings
from tests.conftest import BASE_URL, SAMPLE_SETTINGS


class TestSettings:
    def test_get_returns_settings(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/settings",
            json=SAMPLE_SETTINGS,
            status=200,
        )
        result = client.settings.get()

        assert isinstance(result, Settings)
        assert result.default_webhook_url == "https://example.com/webhook"

    def test_update_returns_settings(self, mock_api, client):
        updated = {"default_webhook_url": "https://new.example.com/hook"}
        mock_api.add(
            responses.PATCH,
            f"{BASE_URL}/api/v1/settings",
            json=updated,
            status=200,
        )
        result = client.settings.update(default_webhook_url="https://new.example.com/hook")

        assert isinstance(result, Settings)
        assert result.default_webhook_url == "https://new.example.com/hook"

    def test_update_sends_body(self, mock_api, client):
        mock_api.add(
            responses.PATCH,
            f"{BASE_URL}/api/v1/settings",
            json=SAMPLE_SETTINGS,
            status=200,
        )
        client.settings.update(default_webhook_url="https://example.com/webhook")

        body = mock_api.calls[0].request.body
        assert b'"default_webhook_url"' in body
