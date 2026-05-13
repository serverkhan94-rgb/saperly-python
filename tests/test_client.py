from __future__ import annotations

import pytest
import responses

from saperly import SaperlyClient, SaperlyError
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

    @responses.activate
    def test_forwards_custom_headers_drops_auth_override(self):
        responses.get(
            f"{BASE_URL}/api/v1/foo",
            json={"ok": True},
            status=200,
        )
        client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
        client._http.request(
            "GET",
            "/foo",
            headers={"X-Custom": "yes", "Authorization": "Bearer EVIL"},
        )

        assert responses.calls[0].request.headers["X-Custom"] == "yes"
        assert responses.calls[0].request.headers["Authorization"] == "Bearer sk_test_xyz"

    def test_rejects_crlf_in_caller_header(self):
        """Defense-in-depth: header injection guard.

        /review hardening (2026-05-12). Underlying requests rejects CRLF too,
        but the SDK raises a named ValueError before the transport sees it.
        """
        import pytest

        client = SaperlyClient(api_key="sk_test_xyz", base_url=BASE_URL)
        with pytest.raises(ValueError, match="CRLF"):
            client._http.request(
                "GET",
                "/foo",
                headers={"X-Inj": "a\r\nAuthorization: Bearer evil"},
            )
        with pytest.raises(ValueError, match="CRLF"):
            client._http.request(
                "GET",
                "/foo",
                headers={"X-Inj\nEvil": "ok"},
            )

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


