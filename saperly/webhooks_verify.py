"""Webhook signature verification for Saperly outbound deliveries.

Every Saperly webhook carries three signed headers:
    - x-saperly-timestamp: unix seconds when the delivery was signed
    - x-saperly-delivery-id: UUID v4, unique per attempt
    - x-saperly-signature: v1=<hex> HMAC-SHA256 over
        ``f"{timestamp}.{delivery_id}.{raw_body}"``

Pure Python implementation — bit-for-bit compatible with the TS
``@saperly/webhook-sig`` package. Parity is enforced via shared test
vectors checked in at ``packages/webhook-sig/test-vectors.json``.

Implementers MUST cache seen ``delivery_id``s for at least the
clock-tolerance window (default 5 minutes) to defeat replay attacks.
This helper cannot dedupe on your behalf because it is stateless.

Example::

    from saperly.webhooks_verify import verify_webhook

    result = verify_webhook(raw_body, os.environ["SAPERLY_WEBHOOK_SECRET"], request.headers)
    if not result.valid:
        return Response(f"Invalid: {result.reason}", status=400)
"""
from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Mapping, Optional

SIGNATURE_VERSION = "v1"
TIMESTAMP_HEADER = "x-saperly-timestamp"
DELIVERY_ID_HEADER = "x-saperly-delivery-id"
SIGNATURE_HEADER = "x-saperly-signature"
DEFAULT_CLOCK_TOLERANCE_SECONDS = 300

VerifyReason = str  # see VerifyResult.reason below


@dataclass(frozen=True)
class VerifyResult:
    """Result of a call to :func:`verify_webhook`.

    ``reason`` values mirror ``@saperly/webhook-sig`` exactly:
    ``missing_timestamp``, ``missing_delivery_id``, ``missing_signature``,
    ``malformed_timestamp``, ``malformed_signature``, ``unknown_version``,
    ``stale_timestamp``, ``signature_mismatch``.
    """

    valid: bool
    reason: Optional[VerifyReason] = None


def _lookup(headers: Mapping[str, str], name: str) -> Optional[str]:
    """Case-insensitive header lookup (RFC 7230)."""
    lower = name.lower()
    for key, value in headers.items():
        if key.lower() == lower:
            return value
    return None


def _compute_signature(body: str, secret: str, timestamp: int, delivery_id: str) -> str:
    payload = f"{timestamp}.{delivery_id}.{body}"
    return hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_webhook(
    raw_body: str,
    secret: str,
    headers: Mapping[str, str],
    *,
    clock_tolerance_seconds: int = DEFAULT_CLOCK_TOLERANCE_SECONDS,
    now: Optional[float] = None,
) -> VerifyResult:
    """Verify a Saperly webhook delivery.

    ``raw_body`` must be the exact request body bytes decoded as UTF-8,
    NOT a re-serialized ``json.dumps(json.loads(...))`` round-trip — any
    whitespace or key-order difference will break the signature.
    """
    ts_raw = _lookup(headers, TIMESTAMP_HEADER)
    if ts_raw is None:
        return VerifyResult(valid=False, reason="missing_timestamp")
    delivery_id = _lookup(headers, DELIVERY_ID_HEADER)
    if delivery_id is None:
        return VerifyResult(valid=False, reason="missing_delivery_id")
    sig_raw = _lookup(headers, SIGNATURE_HEADER)
    if sig_raw is None:
        return VerifyResult(valid=False, reason="missing_signature")

    try:
        timestamp = int(ts_raw)
    except (TypeError, ValueError):
        return VerifyResult(valid=False, reason="malformed_timestamp")
    if timestamp <= 0:
        return VerifyResult(valid=False, reason="malformed_timestamp")

    if "=" not in sig_raw:
        return VerifyResult(valid=False, reason="malformed_signature")
    version, _, provided_hex = sig_raw.partition("=")
    if not provided_hex:
        return VerifyResult(valid=False, reason="malformed_signature")
    if version != SIGNATURE_VERSION:
        return VerifyResult(valid=False, reason="unknown_version")

    expected_hex = _compute_signature(raw_body, secret, timestamp, delivery_id)
    if len(expected_hex) != len(provided_hex):
        return VerifyResult(valid=False, reason="signature_mismatch")
    if not hmac.compare_digest(expected_hex, provided_hex):
        return VerifyResult(valid=False, reason="signature_mismatch")

    # Timestamp check runs AFTER the signature so an attacker cannot
    # distinguish "stale but valid" from "fresh but invalid" by timing.
    now_sec = int(now if now is not None else time.time())
    if abs(now_sec - timestamp) > clock_tolerance_seconds:
        return VerifyResult(valid=False, reason="stale_timestamp")

    return VerifyResult(valid=True)


__all__ = [
    "VerifyResult",
    "verify_webhook",
    "SIGNATURE_VERSION",
    "TIMESTAMP_HEADER",
    "DELIVERY_ID_HEADER",
    "SIGNATURE_HEADER",
    "DEFAULT_CLOCK_TOLERANCE_SECONDS",
]
