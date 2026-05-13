from __future__ import annotations

from typing import Any

from ._client import DEFAULT_BASE_URL
from ._client import AsyncSaperlyClient as _AsyncHttpClient
from ._client import SaperlyClient as _SyncHttpClient
from ._errors import (
    AgentCapExceededError,
    AgentPermissionDeniedError,
    AgentScopeError,
    AuthenticationError,
    CallInProgressError,
    CallNotActiveError,
    ConsentAlreadyGrantedError,
    ConsentRequiredError,
    EmailTakenError,
    ErrorDetail,
    ForbiddenError,
    IdempotencyInProgressError,
    IdempotencyKeyReusedError,
    InsufficientCreditsError,
    M3FraudBlockError,
    MissingIdempotencyKeyError,
    NotFoundError,
    NumberOptedOutError,
    PaymentMethodRequiredError,
    RateLimitedError,
    SaperlyError,
    ValidationError,
)
from ._types import (
    AddFundsResult,
    ApiKey,
    ApiKeyListResult,
    AuditResult,
    Balance,
    Call,
    CallListResult,
    ComplianceEvent,
    ConsentCheckResult,
    ConsentRecord,
    Conversation,
    ConversationListResult,
    ConversationMessage,
    ConversationMessagesResult,
    CreateApiKeyResponse,
    DailyUsage,
    DailyUsageResult,
    DeliveryListResult,
    Disclosure,
    Line,
    Message,
    MonthlyUsage,
    MonthlyUsageResult,
    Settings,
    SmsMessage,
    Transaction,
    TransactionListResult,
    UnifiedAuditEvent,
    UnifiedAuditResult,
    Voice,
    VoiceListResult,
    WebhookDelivery,
    WebhookStats,
    WebhookTestResult,
)
from ._version import __version__
from .resources.audit import AsyncAuditResource, AuditResource
from .resources.billing import AsyncBillingResource, BillingResource
from .resources.calls import AsyncCallsResource, CallsResource
from .resources.compliance import AsyncComplianceResource, ComplianceResource
from .resources.consent import AsyncConsentResource, ConsentResource
from .resources.conversations import AsyncConversationsResource, ConversationsResource
from .resources.disclosures import AsyncDisclosuresResource, DisclosuresResource
from .resources.keys import AsyncKeysResource, KeysResource
from .resources.lines import AsyncLinesResource, LinesResource
from .resources.messages import AsyncMessagesResource, MessagesResource
from .resources.settings import AsyncSettingsResource, SettingsResource
from .resources.usage import AsyncUsageResource, UsageResource
from .resources.voices import AsyncVoicesResource, VoicesResource
from .resources.webhooks import AsyncWebhooksResource, WebhooksResource
from .webhooks_verify import VerifyResult, verify_webhook


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
        self.audit = AuditResource(self._http)
        self.disclosures = DisclosuresResource(self._http)
        self.billing = BillingResource(self._http)
        self.webhooks = WebhooksResource(self._http)
        self.messages = MessagesResource(self._http)
        self.conversations = ConversationsResource(self._http)
        self.usage = UsageResource(self._http)
        self.settings = SettingsResource(self._http)
        self.voices = VoicesResource(self._http)
        self.keys = KeysResource(self._http)

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
        self.audit = AsyncAuditResource(self._http)
        self.disclosures = AsyncDisclosuresResource(self._http)
        self.billing = AsyncBillingResource(self._http)
        self.webhooks = AsyncWebhooksResource(self._http)
        self.messages = AsyncMessagesResource(self._http)
        self.conversations = AsyncConversationsResource(self._http)
        self.usage = AsyncUsageResource(self._http)
        self.settings = AsyncSettingsResource(self._http)
        self.voices = AsyncVoicesResource(self._http)
        self.keys = AsyncKeysResource(self._http)

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
    "UnifiedAuditEvent",
    "UnifiedAuditResult",
    "AuditResource",
    "AsyncAuditResource",
    "DeliveryListResult",
    "Transaction",
    "TransactionListResult",
    "AddFundsResult",
    "Message",
    "Conversation",
    "ConversationListResult",
    "ConversationMessage",
    "ConversationMessagesResult",
    "DailyUsage",
    "DailyUsageResult",
    "MonthlyUsage",
    "MonthlyUsageResult",
    "Settings",
    "Voice",
    "VoiceListResult",
    "ApiKey",
    "ApiKeyListResult",
    "CreateApiKeyResponse",
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
    "PaymentMethodRequiredError",
    "NumberOptedOutError",
    "EmailTakenError",
    "RateLimitedError",
    "AgentScopeError",
    "AgentCapExceededError",
    "AgentPermissionDeniedError",
    "M3FraudBlockError",
    "IdempotencyKeyReusedError",
    "IdempotencyInProgressError",
    "MissingIdempotencyKeyError",
    # Webhook verification
    "verify_webhook",
    "VerifyResult",
]
