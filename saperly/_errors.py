from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ErrorDetail:
    message: str
    field: Optional[str] = None


class SaperlyError(Exception):
    """Base error for all Saperly API errors."""

    def __init__(
        self,
        code: str,
        status: int,
        message: str,
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        self.details: List[ErrorDetail] = details or []

    @staticmethod
    def from_response(status: int, body: object) -> SaperlyError:
        """Create the appropriate error subclass from an API error response."""
        parsed = body if isinstance(body, dict) else {}
        error_obj = parsed.get("error", {}) if isinstance(parsed, dict) else {}
        if not isinstance(error_obj, dict):
            error_obj = {}

        code: str = error_obj.get("code", "unknown")
        message: str = error_obj.get("message", "An unexpected error occurred")
        raw_details = error_obj.get("details", [])

        details: List[ErrorDetail] = []
        if isinstance(raw_details, list):
            for d in raw_details:
                if isinstance(d, dict):
                    details.append(
                        ErrorDetail(
                            message=d.get("message", ""),
                            field=d.get("field"),
                        )
                    )

        _MAP = {
            "validation_error": lambda: ValidationError(message, status, details),
            "invalid_api_key": lambda: AuthenticationError(message, status),
            "unauthorized": lambda: AuthenticationError(message, status),
            "forbidden": lambda: ForbiddenError(message, status),
            "not_found": lambda: NotFoundError(message, status),
            "call_not_found": lambda: NotFoundError(message, status),
            "consent_required": lambda: ConsentRequiredError(message, status),
            "consent_already_granted": lambda: ConsentAlreadyGrantedError(message, status),
            "call_in_progress": lambda: CallInProgressError(message, status),
            "call_not_active": lambda: CallNotActiveError(message, status),
            "insufficient_credits": lambda: InsufficientCreditsError(message, status),
            "payment_method_required": lambda: PaymentMethodRequiredError(message, status),
            "number_opted_out": lambda: NumberOptedOutError(message, status),
            "email_taken": lambda: EmailTakenError(message, status),
            "rate_limited": lambda: RateLimitedError(message, status),
            "agent_scope_error": lambda: AgentScopeError(message, status, details),
            "agent_cap_exceeded": lambda: AgentCapExceededError(message, status, details),
            "agent_permission_denied": lambda: AgentPermissionDeniedError(
                message, status, details
            ),
            "m3_fraud_block": lambda: M3FraudBlockError(message, status),
            "idempotency_key_reused": lambda: IdempotencyKeyReusedError(message, status),
            "idempotency_in_progress": lambda: IdempotencyInProgressError(message, status),
            "missing_idempotency_key": lambda: MissingIdempotencyKeyError(message, status),
        }

        factory = _MAP.get(code)
        if factory is not None:
            return factory()
        return SaperlyError(code, status, message, details)


class ValidationError(SaperlyError):
    def __init__(
        self,
        message: str,
        status: int = 422,
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__("validation_error", status, message, details)


class AuthenticationError(SaperlyError):
    def __init__(self, message: str, status: int = 401) -> None:
        super().__init__("invalid_api_key", status, message)


class ForbiddenError(SaperlyError):
    def __init__(self, message: str, status: int = 403) -> None:
        super().__init__("forbidden", status, message)


class NotFoundError(SaperlyError):
    def __init__(self, message: str, status: int = 404) -> None:
        super().__init__("not_found", status, message)


class ConsentRequiredError(SaperlyError):
    def __init__(self, message: str, status: int = 403) -> None:
        super().__init__("consent_required", status, message)


class ConsentAlreadyGrantedError(SaperlyError):
    def __init__(self, message: str, status: int = 409) -> None:
        super().__init__("consent_already_granted", status, message)


class CallInProgressError(SaperlyError):
    def __init__(self, message: str, status: int = 409) -> None:
        super().__init__("call_in_progress", status, message)


class CallNotActiveError(SaperlyError):
    def __init__(self, message: str, status: int = 409) -> None:
        super().__init__("call_not_active", status, message)


class InsufficientCreditsError(SaperlyError):
    def __init__(self, message: str, status: int = 402) -> None:
        super().__init__("insufficient_credits", status, message)


class PaymentMethodRequiredError(SaperlyError):
    """Raised when POST /v1/lines requires a payment method on file.

    Triggered when ``users.firstLineProvisionedAt`` is non-null AND
    ``billing_accounts.has_default_pm`` is false. The first-ever line is
    frictionless; line #2+ in live env requires a card. Add a payment method
    in the Saperly portal at https://saperly.com/billing#payment-method, then
    retry with a NEW Idempotency-Key (the original 402 is sticky-cached for
    ~12h).
    """

    def __init__(self, message: str, status: int = 402) -> None:
        super().__init__("payment_method_required", status, message)


class NumberOptedOutError(SaperlyError):
    def __init__(self, message: str, status: int = 403) -> None:
        super().__init__("number_opted_out", status, message)


class EmailTakenError(SaperlyError):
    def __init__(self, message: str, status: int = 409) -> None:
        super().__init__("email_taken", status, message)


class RateLimitedError(SaperlyError):
    def __init__(self, message: str, status: int = 429) -> None:
        super().__init__("rate_limited", status, message)


class AgentScopeError(SaperlyError):
    """v0.5.6.0 (M1 PR1) — line-scoped key tried to act on a different line.

    Server emits structured detail: ``line_id`` (the requested line).
    403 status (not 404) — the line may exist; the key just isn't authorized.
    """

    def __init__(
        self,
        message: str,
        status: int = 403,
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__("agent_scope_error", status, message, details)


class AgentCapExceededError(SaperlyError):
    """v0.5.6.0 (M1 PR1) — agent monthly_cap_cents reached.

    Server emits structured details: ``spent_cents``, ``cap_cents``,
    ``cycle_reset_at``. 402 status — same family as InsufficientCreditsError;
    catch both to render a unified "fund or raise cap" message.
    """

    def __init__(
        self,
        message: str,
        status: int = 402,
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__("agent_cap_exceeded", status, message, details)


class AgentPermissionDeniedError(SaperlyError):
    """v0.5.6.0 (M1 PR1) — permission tier denied for verb.

    Server emits structured detail: ``permissions = "tier=X verb=Y"``.
    403 (not 401) — auth succeeded; tier just lacks the verb.
    """

    def __init__(
        self,
        message: str,
        status: int = 403,
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__("agent_permission_denied", status, message, details)


class M3FraudBlockError(SaperlyError):
    """v0.5.6.0 (M3 PR2) — request matched an IRSF-reconnaissance pattern.

    Customer-facing copy is intentionally vague AND server emits no details
    (per fraud-heuristic.ts comment) — do not treat empty details as a bug.
    """

    def __init__(self, message: str, status: int = 403) -> None:
        super().__init__("m3_fraud_block", status, message)


class IdempotencyKeyReusedError(SaperlyError):
    """Idempotency-Key reused with a different request body within 24h.

    Recovery: use a NEW Idempotency-Key for the new request body.
    """

    def __init__(self, message: str, status: int = 409) -> None:
        super().__init__("idempotency_key_reused", status, message)


class IdempotencyInProgressError(SaperlyError):
    """A request with this Idempotency-Key is still in progress.

    Retry after the server-supplied Retry-After window (default 1s).
    """

    def __init__(self, message: str, status: int = 409) -> None:
        super().__init__("idempotency_in_progress", status, message)


class MissingIdempotencyKeyError(SaperlyError):
    """A POST that requires an Idempotency-Key header was sent without one.

    The SDK auto-generates UUID v4 keys for /v1/keys mints and rotates, so
    this only surfaces if a caller bypasses the SDK helpers.
    """

    def __init__(self, message: str, status: int = 400) -> None:
        super().__init__("missing_idempotency_key", status, message)
