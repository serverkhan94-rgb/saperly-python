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
