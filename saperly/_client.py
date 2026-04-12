from __future__ import annotations

import asyncio
import time
import urllib.parse
from typing import Any, Dict, Optional

import requests

from ._errors import SaperlyError
from ._transforms import to_snake_keys

DEFAULT_BASE_URL = "https://saperly-production.up.railway.app"
_API_PREFIX = "/api/v1"


def _build_url(
    base_url: str,
    path: str,
    query: Optional[Dict[str, Any]] = None,
) -> str:
    url = f"{base_url}{_API_PREFIX}{path}"
    if query:
        filtered = {k: str(v) for k, v in query.items() if v is not None}
        if filtered:
            url = f"{url}?{urllib.parse.urlencode(filtered)}"
    return url


def _build_headers(api_key: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def _raise_for_error(status: int, body: object) -> None:
    raise SaperlyError.from_response(status, body)


_RETRYABLE_METHODS = frozenset({"GET", "DELETE", "HEAD", "OPTIONS"})


class SaperlyClient:
    """Synchronous HTTP client for the Saperly API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        url = _build_url(self._base_url, path, query)
        headers = _build_headers(self._api_key)

        is_retryable = method.upper() in _RETRYABLE_METHODS
        max_attempts = 2 if is_retryable else 1
        last_error: Optional[Exception] = None

        for attempt in range(1, max_attempts + 1):
            try:
                resp = self._session.request(
                    method,
                    url,
                    headers=headers,
                    json=body,
                    timeout=self._timeout,
                )

                if resp.status_code >= 500 and is_retryable and attempt < max_attempts:
                    time.sleep(1)
                    continue

                if resp.status_code >= 400:
                    try:
                        error_body = resp.json()
                    except ValueError:
                        error_body = None
                    _raise_for_error(resp.status_code, error_body)

                if resp.status_code == 204:
                    return None

                data = resp.json()
                return to_snake_keys(data)
            except SaperlyError:
                raise
            except (requests.ConnectionError, requests.Timeout) as exc:
                last_error = exc
                if is_retryable and attempt < max_attempts:
                    time.sleep(1)
                    continue
                raise

        if last_error:
            raise last_error

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> SaperlyClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncSaperlyClient:
    """Asynchronous HTTP client for the Saperly API (requires httpx)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        try:
            import httpx  # noqa: F401
        except ImportError:
            raise ImportError(
                "Install saperly[async]: pip install saperly[async]"
            ) from None

        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Any:
        import httpx

        url = _build_url(self._base_url, path, query)
        headers = _build_headers(self._api_key)

        is_retryable = method.upper() in _RETRYABLE_METHODS
        max_attempts = 2 if is_retryable else 1
        last_error: Optional[Exception] = None

        for attempt in range(1, max_attempts + 1):
            try:
                resp = await self._client.request(
                    method,
                    url,
                    headers=headers,
                    json=body,
                )

                if resp.status_code >= 500 and is_retryable and attempt < max_attempts:
                    await asyncio.sleep(1)
                    continue

                if resp.status_code >= 400:
                    try:
                        error_body = resp.json()
                    except ValueError:
                        error_body = None
                    _raise_for_error(resp.status_code, error_body)

                if resp.status_code == 204:
                    return None

                data = resp.json()
                return to_snake_keys(data)
            except SaperlyError:
                raise
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                last_error = exc
                if is_retryable and attempt < max_attempts:
                    await asyncio.sleep(1)
                    continue
                raise

        if last_error:
            raise last_error

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncSaperlyClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()
