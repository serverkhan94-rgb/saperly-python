from __future__ import annotations

import json

import pytest
import responses

from saperly import EmailTakenError, SaperlyClient, SaperlyError, ValidationError
from tests.conftest import BASE_URL, SAMPLE_LINE, SAMPLE_STATS_RAW


class TestSyncClient:
    def test_sets_auth_header(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/api/v1/lines",
                json={"lines": [SAMPLE_LINE]},
                status=200,
            )
            client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
            client.lines.list()

            assert rsps.calls[0].request.headers["Authorization"] == "Bearer sk_test_123"

    def test_uses_custom_base_url(self):
        custom_url = "http://custom-host:9000"
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{custom_url}/api/v1/lines",
                json={"lines": []},
                status=200,
            )
            client = SaperlyClient(api_key="sk_test_123", base_url=custom_url)
            client.lines.list()

            assert rsps.calls[0].request.url == f"{custom_url}/api/v1/lines"

    def test_empty_api_key_raises(self):
        with pytest.raises(ValueError, match="api_key is required"):
            SaperlyClient(api_key="", base_url=BASE_URL)

    def test_204_returns_none(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.DELETE,
                f"{BASE_URL}/api/v1/some-resource",
                status=204,
            )
            client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
            result = client._http.request("DELETE", "/some-resource")

            assert result is None

    def test_non_json_error_body(self):
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/api/v1/lines",
                body="Internal Server Error",
                status=500,
                content_type="text/plain",
            )
            client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)

            with pytest.raises(SaperlyError) as exc_info:
                client.lines.list()
            assert exc_info.value.code == "unknown"
            assert exc_info.value.status == 500

    def test_response_transform(self):
        """Verify camelCase keys in response get converted to snake_case."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{BASE_URL}/api/v1/webhooks/stats",
                json=SAMPLE_STATS_RAW,
                status=200,
            )
            client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
            stats = client.webhooks.stats()

            assert stats.success_rate == 0.95
            assert stats.by_event_type is not None
            assert stats.by_event_type[0]["event_type"] == "call_started"
            assert stats.by_hour is not None
            assert stats.by_hour[0]["hour"] == "2026-01-01T00:00:00Z"


class TestRegister:
    @responses.activate
    def test_register_success(self):
        responses.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json={
                "user": {
                    "id": "uuid-123",
                    "email": "test@example.com",
                    "name": None,
                    "created_at": "2026-01-01T00:00:00Z",
                },
            },
            status=201,
        )
        result = SaperlyClient.register(
            email="test@example.com",
            password="securepass123",
            base_url=BASE_URL,
        )

        assert result["user"]["id"] == "uuid-123"
        assert result["user"]["email"] == "test@example.com"

        body = json.loads(responses.calls[0].request.body)
        assert body["email"] == "test@example.com"
        assert body["password"] == "securepass123"

    @responses.activate
    def test_register_email_taken(self):
        responses.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json={"error": {"code": "email_taken", "message": "Email already registered"}},
            status=409,
        )
        with pytest.raises(EmailTakenError):
            SaperlyClient.register(
                email="taken@example.com",
                password="securepass123",
                base_url=BASE_URL,
            )

    @responses.activate
    def test_register_validation_error(self):
        responses.post(
            f"{BASE_URL}/api/v1/auth/signup",
            json={"error": {"code": "validation_error", "message": "Password too short"}},
            status=422,
        )
        with pytest.raises(ValidationError):
            SaperlyClient.register(
                email="test@example.com",
                password="short",
                base_url=BASE_URL,
            )
