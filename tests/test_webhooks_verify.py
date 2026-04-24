"""Parity tests for saperly.webhooks_verify.

Shares ``packages/webhook-sig/test-vectors.json`` with the canonical TS
implementation. Any drift between the two impls — Python here, TS in
``packages/webhook-sig`` — will surface as a parity-test failure.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from pathlib import Path

import pytest

from saperly.webhooks_verify import (
    DELIVERY_ID_HEADER,
    SIGNATURE_HEADER,
    SIGNATURE_VERSION,
    TIMESTAMP_HEADER,
    VerifyResult,
    verify_webhook,
)

# Canonical vectors live in the TS package.
VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "packages"
    / "webhook-sig"
    / "test-vectors.json"
)


def _build_headers(vector: dict) -> dict:
    return {
        TIMESTAMP_HEADER: str(vector["timestamp"]),
        DELIVERY_ID_HEADER: vector["delivery_id"],
        SIGNATURE_HEADER: f"{SIGNATURE_VERSION}={vector['expected_signature_hex']}",
    }


def _compute_hex(body: str, secret: str, timestamp: int, delivery_id: str) -> str:
    payload = f"{timestamp}.{delivery_id}.{body}".encode("utf-8")
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


def _load_vectors() -> list[dict]:
    with VECTORS_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data["vectors"]


@pytest.fixture(scope="module")
def vectors() -> list[dict]:
    return _load_vectors()


def test_python_hmac_matches_canonical_vectors(vectors: list[dict]) -> None:
    """Python's HMAC must produce the exact hex stored in the shared vectors."""
    for vector in vectors:
        produced = _compute_hex(
            vector["body"],
            vector["secret"],
            vector["timestamp"],
            vector["delivery_id"],
        )
        assert produced == vector["expected_signature_hex"], (
            f"Drift on vector {vector['name']!r}: "
            f"Python produced {produced!r}, "
            f"vectors say {vector['expected_signature_hex']!r}"
        )


def test_verify_webhook_accepts_every_canonical_vector(vectors: list[dict]) -> None:
    """Full ``verify_webhook`` round-trip for every shared vector."""
    for vector in vectors:
        headers = _build_headers(vector)
        result = verify_webhook(
            vector["body"],
            vector["secret"],
            headers,
            now=float(vector["timestamp"]),  # pin clock inside the 5-min window
        )
        assert result.valid, (
            f"Vector {vector['name']!r} failed verification: {result.reason!r}"
        )


def test_verify_rejects_tampered_body(vectors: list[dict]) -> None:
    vector = vectors[0]
    headers = _build_headers(vector)
    tampered = vector["body"] + " tampered"
    result = verify_webhook(
        tampered,
        vector["secret"],
        headers,
        now=float(vector["timestamp"]),
    )
    assert result == VerifyResult(valid=False, reason="signature_mismatch")


def test_verify_rejects_tampered_delivery_id(vectors: list[dict]) -> None:
    vector = vectors[0]
    headers = _build_headers(vector)
    headers[DELIVERY_ID_HEADER] = "00000000-0000-4000-8000-000000000000"
    result = verify_webhook(
        vector["body"],
        vector["secret"],
        headers,
        now=float(vector["timestamp"]),
    )
    assert result == VerifyResult(valid=False, reason="signature_mismatch")


def test_verify_rejects_missing_headers(vectors: list[dict]) -> None:
    vector = vectors[0]
    for header in (TIMESTAMP_HEADER, DELIVERY_ID_HEADER, SIGNATURE_HEADER):
        headers = _build_headers(vector)
        del headers[header]
        result = verify_webhook(
            vector["body"],
            vector["secret"],
            headers,
            now=float(vector["timestamp"]),
        )
        assert not result.valid
        assert result.reason == f"missing_{header.split('-', 2)[-1].replace('-', '_')}"


def test_verify_rejects_stale_timestamp(vectors: list[dict]) -> None:
    vector = vectors[0]
    headers = _build_headers(vector)
    result = verify_webhook(
        vector["body"],
        vector["secret"],
        headers,
        now=float(vector["timestamp"]) + 10 * 60,  # 10 min in the future
    )
    assert result == VerifyResult(valid=False, reason="stale_timestamp")


def test_verify_rejects_unknown_signature_version(vectors: list[dict]) -> None:
    vector = vectors[0]
    headers = _build_headers(vector)
    headers[SIGNATURE_HEADER] = f"v2={vector['expected_signature_hex']}"
    result = verify_webhook(
        vector["body"],
        vector["secret"],
        headers,
        now=float(vector["timestamp"]),
    )
    assert result == VerifyResult(valid=False, reason="unknown_version")


def test_verify_rejects_malformed_timestamp(vectors: list[dict]) -> None:
    vector = vectors[0]
    headers = _build_headers(vector)
    headers[TIMESTAMP_HEADER] = "not-a-number"
    result = verify_webhook(
        vector["body"],
        vector["secret"],
        headers,
    )
    assert result == VerifyResult(valid=False, reason="malformed_timestamp")


def test_verify_rejects_malformed_signature(vectors: list[dict]) -> None:
    vector = vectors[0]
    headers = _build_headers(vector)
    headers[SIGNATURE_HEADER] = "not-a-valid-signature"
    result = verify_webhook(
        vector["body"],
        vector["secret"],
        headers,
        now=float(vector["timestamp"]),
    )
    assert result == VerifyResult(valid=False, reason="malformed_signature")


def test_verify_accepts_case_insensitive_headers(vectors: list[dict]) -> None:
    vector = vectors[0]
    upper = {
        "X-Saperly-Timestamp": str(vector["timestamp"]),
        "X-Saperly-Delivery-Id": vector["delivery_id"],
        "X-Saperly-Signature": f"{SIGNATURE_VERSION}={vector['expected_signature_hex']}",
    }
    result = verify_webhook(
        vector["body"],
        vector["secret"],
        upper,
        now=float(vector["timestamp"]),
    )
    assert result.valid is True


def test_verify_uses_default_now_when_unspecified(vectors: list[dict]) -> None:
    """Sanity check: without an injected clock, a fresh signature verifies."""
    # Use the current time so the signature is always in-window.
    now = int(time.time())
    body = "{}"
    secret = "test-secret"
    delivery_id = "00000000-0000-4000-8000-000000000000"
    signature_hex = _compute_hex(body, secret, now, delivery_id)
    headers = {
        TIMESTAMP_HEADER: str(now),
        DELIVERY_ID_HEADER: delivery_id,
        SIGNATURE_HEADER: f"{SIGNATURE_VERSION}={signature_hex}",
    }
    result = verify_webhook(body, secret, headers)
    assert result.valid is True
