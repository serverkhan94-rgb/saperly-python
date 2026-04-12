from __future__ import annotations

import httpx
import pytest
import respx

from saperly import AsyncSaperlyClient
from tests.conftest import BASE_URL, SAMPLE_LINE


class TestAsyncClient:
    @respx.mock
    async def test_sets_auth_header(self):
        route = respx.get(f"{BASE_URL}/api/v1/lines").mock(
            return_value=httpx.Response(200, json={"lines": [SAMPLE_LINE]}),
        )
        client = AsyncSaperlyClient(api_key="sk_test_async", base_url=BASE_URL)
        await client.lines.list()

        assert route.called
        request = route.calls[0].request
        assert request.headers["Authorization"] == "Bearer sk_test_async"
        await client.aclose()

    @respx.mock
    async def test_uses_custom_base_url(self):
        custom_url = "http://custom-async:8080"
        route = respx.get(f"{custom_url}/api/v1/lines").mock(
            return_value=httpx.Response(200, json={"lines": []}),
        )
        client = AsyncSaperlyClient(api_key="sk_test_async", base_url=custom_url)
        await client.lines.list()

        assert route.called
        assert str(route.calls[0].request.url) == f"{custom_url}/api/v1/lines"
        await client.aclose()

    def test_empty_api_key_raises(self):
        with pytest.raises(ValueError, match="api_key is required"):
            AsyncSaperlyClient(api_key="", base_url=BASE_URL)

    @respx.mock
    async def test_204_returns_none(self):
        respx.delete(f"{BASE_URL}/api/v1/some-resource").mock(
            return_value=httpx.Response(204),
        )
        client = AsyncSaperlyClient(api_key="sk_test_async", base_url=BASE_URL)
        result = await client._http.request("DELETE", "/some-resource")

        assert result is None
        await client.aclose()
