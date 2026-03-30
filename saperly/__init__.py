from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from ._client import DEFAULT_BASE_URL
from ._client import AsyncSaperlyClient as _AsyncHttpClient
from ._client import SaperlyClient as _SyncHttpClient
from ._errors import (
    AuthenticationError,
    CallInProgressError,
    CallNotActiveError,
    ConsentAlreadyGrantedError,
    ConsentRequiredError,
    EmailTakenError,
    ErrorDetail,
    ForbiddenError,
    InsufficientCreditsError,
    NotFoundError,
    NumberOptedOutError,
    RateLimitedError,
    SaperlyError,
    ValidationError,
)
from ._transforms import to_snake_keys
from ._types import (
    AuditResult,
    Balance,
    Call,
    CallListResult,
    ComplianceEvent,
    ConsentCheckResult,
    ConsentRecord,
    DeliveryListResult,
    Disclosure,
    Line,
    SmsMessage,
    WebhookDelivery,
    WebhookStats,
    WebhookTestResult,
)
from ._version import __version__
from .resources.billing import AsyncBillingResource, BillingResource
from .resources.calls import AsyncCallsResource, CallsResource
from .resources.compliance import AsyncComplianceResource, ComplianceResource
from .resources.consent import AsyncConsentResource, ConsentResource
from .resources.disclosures import AsyncDisclosuresResource, DisclosuresResource
from .resources.lines import AsyncLinesResource, LinesResource
from .resources.webhooks import AsyncWebhooksResource, WebhooksResource


class SaperlyClient:
    """Synchronous Saperly SDK client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._http = _SyncHttpClient(api_key, base_url, timeout)
        self.lines = LinesResource(self._http)
        self.calls = CallsResource(self._http)
        self.consent = ConsentResource(self._http)
        self.compliance = ComplianceResource(self._http)
        self.disclosures = DisclosuresResource(self._http)
        self.billing = BillingResource(self._http)
        self.webhooks = WebhooksResource(self._http)

    @staticmethod
    def register(
        *,
        email: str,
        password: str,
        name: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> Dict[str, Any]:
        """Programmatic signup. Creates account + default test API key."""
        url = f"{base_url}/api/v1/auth/signup"
        body: Dict[str, Any] = {"email": email, "password": password}
        if name is not None:
            body["name"] = name
        resp = requests.post(
            url,
            json=body,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )
        if resp.status_code >= 400:
            try:
                error_body = resp.json()
            except ValueError:
                error_body = None
            raise SaperlyError.from_response(resp.status_code, error_body)
        data: object = resp.json()
        return to_snake_keys(data)  # type: ignore[return-value]

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SaperlyClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncSaperlyClient:
    """Asynchronous Saperly SDK client (requires httpx)."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ) -> None:
        self._http = _AsyncHttpClient(api_key, base_url, timeout)
        self.lines = AsyncLinesResource(self._http)
        self.calls = AsyncCallsResource(self._http)
        self.consent = AsyncConsentResource(self._http)
        self.compliance = AsyncComplianceResource(self._http)
        self.disclosures = AsyncDisclosuresResource(self._http)
        self.billing = AsyncBillingResource(self._http)
        self.webhooks = AsyncWebhooksResource(self._http)

    @staticmethod
    async def register(
        *,
        email: str,
        password: str,
        name: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
    ) -> Dict[str, Any]:
        """Programmatic signup. Creates account + default test API key."""
        import httpx

        url = f"{base_url}/api/v1/auth/signup"
        body: Dict[str, Any] = {"email": email, "password": password}
        if name is not None:
            body["name"] = name
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                json=body,
                headers={"Content-Type": "application/json"},
            )
        if resp.status_code >= 400:
            try:
                error_body = resp.json()
            except ValueError:
                error_body = None
            raise SaperlyError.from_response(resp.status_code, error_body)
        data: object = resp.json()
        return to_snake_keys(data)  # type: ignore[return-value]

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncSaperlyClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.aclose()


__all__ = [
    # Clients
    "SaperlyClient",
    "AsyncSaperlyClient",
    # Version
    "__version__",
    # Types
    "Line",
    "Call",
    "ConsentRecord",
    "ConsentCheckResult",
    "ComplianceEvent",
    "Disclosure",
    "Balance",
    "SmsMessage",
    "WebhookDelivery",
    "WebhookStats",
    "WebhookTestResult",
    "CallListResult",
    "AuditResult",
    "DeliveryListResult",
    # Errors
    "SaperlyError",
    "ErrorDetail",
    "ValidationError",
    "AuthenticationError",
    "ForbiddenError",
    "NotFoundError",
    "ConsentRequiredError",
    "ConsentAlreadyGrantedError",
    "CallInProgressError",
    "CallNotActiveError",
    "InsufficientCreditsError",
    "NumberOptedOutError",
    "EmailTakenError",
    "RateLimitedError",
]
