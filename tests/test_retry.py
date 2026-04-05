from __future__ import annotations

from unittest.mock import AsyncMock, patch

import httpx
import pytest
import requests
import responses
import respx

from saperly import AsyncSaperlyClient, SaperlyClient, SaperlyError
from tests.conftest import BASE_URL


class TestSyncRetry:
    @responses.activate
    @patch("saperly._client.time.sleep")
    def test_get_500_then_200_retries(self, mock_sleep):
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            json={"error": {"code": "internal_error", "message": "fail"}},
            status=500,
        )
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            json={"lines": []},
            status=200,
        )
        client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        result = client.lines.list()

        assert len(responses.calls) == 2
        assert result == []
        mock_sleep.assert_called_once_with(1)

    @responses.activate
    def test_post_500_no_retry(self):
        responses.post(
            f"{BASE_URL}/api/v1/lines",
            json={"error": {"code": "internal_error", "message": "fail"}},
            status=500,
        )
        client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)

        with pytest.raises(SaperlyError) as exc_info:
            client.lines.create(name="test", mode="text")
        assert exc_info.value.status == 500
        assert len(responses.calls) == 1

    @responses.activate
    @patch("saperly._client.time.sleep")
    def test_get_500_twice_throws(self, mock_sleep):
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            json={"error": {"code": "internal_error", "message": "fail"}},
            status=500,
        )
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            json={"error": {"code": "internal_error", "message": "fail"}},
            status=500,
        )
        client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)

        with pytest.raises(SaperlyError) as exc_info:
            client.lines.list()
        assert exc_info.value.status == 500
        assert len(responses.calls) == 2

    @responses.activate
    @patch("saperly._client.time.sleep")
    def test_get_connection_error_retries(self, mock_sleep):
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            body=requests.ConnectionError("refused"),
        )
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            json={"lines": []},
            status=200,
        )
        client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        result = client.lines.list()

        assert len(responses.calls) == 2
        assert result == []

    @responses.activate
    @patch("saperly._client.time.sleep")
    def test_delete_502_retries(self, mock_sleep):
        responses.delete(
            f"{BASE_URL}/api/v1/lines/line-1",
            json={"error": {"code": "internal_error", "message": "fail"}},
            status=502,
        )
        responses.delete(
            f"{BASE_URL}/api/v1/lines/line-1",
            json={"line": {"id": "line-1", "phone_number": "+1"}},
            status=200,
        )
        client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        result = client.lines.delete("line-1")

        assert len(responses.calls) == 2
        assert result.id == "line-1"

    @responses.activate
    @patch("saperly._client.time.sleep")
    def test_get_timeout_retries(self, mock_sleep):
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            body=requests.Timeout("timed out"),
        )
        responses.get(
            f"{BASE_URL}/api/v1/lines",
            json={"lines": []},
            status=200,
        )
        client = SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        result = client.lines.list()

        assert len(responses.calls) == 2
        assert result == []
        mock_sleep.assert_called_once_with(1)


class TestAsyncRetry:
    @respx.mock
    async def test_async_get_500_then_200(self):
        route = respx.get(f"{BASE_URL}/api/v1/lines")
        route.side_effect = [
            httpx.Response(500, json={"error": {"code": "internal_error", "message": "fail"}}),
            httpx.Response(200, json={"lines": []}),
        ]
        client = AsyncSaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        with patch("saperly._client.asyncio.sleep", new_callable=AsyncMock):
            result = await client.lines.list()

        assert route.call_count == 2
        assert result == []
        await client.aclose()

    @respx.mock
    async def test_async_post_500_no_retry(self):
        route = respx.post(f"{BASE_URL}/api/v1/lines")
        route.side_effect = [
            httpx.Response(500, json={"error": {"code": "internal_error", "message": "fail"}}),
        ]
        client = AsyncSaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        with pytest.raises(SaperlyError) as exc_info:
            await client.lines.create(name="test", mode="text")
        assert exc_info.value.status == 500
        assert route.call_count == 1
        await client.aclose()

    @respx.mock
    async def test_async_get_500_twice_throws(self):
        route = respx.get(f"{BASE_URL}/api/v1/lines")
        route.side_effect = [
            httpx.Response(500, json={"error": {"code": "internal_error", "message": "fail"}}),
            httpx.Response(500, json={"error": {"code": "internal_error", "message": "fail"}}),
        ]
        client = AsyncSaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        with patch("saperly._client.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(SaperlyError) as exc_info:
                await client.lines.list()
        assert exc_info.value.status == 500
        assert route.call_count == 2
        await client.aclose()

    @respx.mock
    async def test_async_get_connection_error_retries(self):
        route = respx.get(f"{BASE_URL}/api/v1/lines")
        route.side_effect = [
            httpx.ConnectError("refused"),
            httpx.Response(200, json={"lines": []}),
        ]
        client = AsyncSaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        with patch("saperly._client.asyncio.sleep", new_callable=AsyncMock):
            result = await client.lines.list()
        assert route.call_count == 2
        assert result == []
        await client.aclose()

    @respx.mock
    async def test_async_delete_502_retries(self):
        route = respx.delete(f"{BASE_URL}/api/v1/lines/line-1")
        route.side_effect = [
            httpx.Response(502, json={"error": {"code": "internal_error", "message": "fail"}}),
            httpx.Response(200, json={"line": {"id": "line-1", "phone_number": "+1"}}),
        ]
        client = AsyncSaperlyClient(api_key="sk_test_123", base_url=BASE_URL)
        with patch("saperly._client.asyncio.sleep", new_callable=AsyncMock):
            result = await client.lines.delete("line-1")
        assert route.call_count == 2
        assert result.id == "line-1"
        await client.aclose()
