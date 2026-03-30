from __future__ import annotations

import pytest
import responses

from saperly import SaperlyClient

BASE_URL = "http://test"


@pytest.fixture
def mock_api():
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def client():
    return SaperlyClient(api_key="sk_test_123", base_url=BASE_URL)


# ---------------------------------------------------------------------------
# Sample data constants (snake_case — matching post-transform API responses)
# ---------------------------------------------------------------------------

SAMPLE_LINE = {
    "id": "line-1",
    "phone_number": "+14155550123",
    "display_name": None,
    "name": "support",
    "mode": "text",
    "audio_handler_url": None,
    "webhook_url": "https://example.com/hook",
    "status_callback_url": None,
    "status": "active",
    "environment": "live",
    "created_at": "2026-01-01T00:00:00Z",
}

SAMPLE_CALL = {
    "id": "call-1",
    "line_id": "line-1",
    "direction": "outbound",
    "from_number": "+14155550123",
    "to_number": "+14155559999",
    "status": "initiated",
    "duration_sec": None,
    "started_at": None,
    "ended_at": None,
    "created_at": "2026-01-01T00:00:00Z",
}

SAMPLE_CONSENT = {
    "id": "consent-1",
    "phone_number": "+14155559999",
    "line_id": "line-1",
    "consent_type": "explicit_outbound",
    "status": "active",
    "granted_at": "2026-01-01T00:00:00Z",
    "revoked_at": None,
}

SAMPLE_EVENT = {
    "id": "event-1",
    "line_id": "line-1",
    "call_id": "call-1",
    "phone_number": "+14155559999",
    "event_type": "call_started",
    "metadata": {"source": "outbound"},
    "created_at": "2026-01-01T00:00:00Z",
}

SAMPLE_DISCLOSURE = {
    "id": "disc-1",
    "message": "This call uses AI.",
    "audio_url": None,
    "language": "en",
    "jurisdiction": "us",
    "is_default": True,
    "created_at": "2026-01-01T00:00:00Z",
}

SAMPLE_DELIVERY = {
    "id": "del-1",
    "line_id": "line-1",
    "call_id": "call-1",
    "event_type": "call_started",
    "url": "https://example.com/hook",
    "status": "success",
    "http_status": 200,
    "error_message": None,
    "attempt_count": 1,
    "request_body": {},
    "response_body": "ok",
    "duration_ms": 150,
    "created_at": "2026-01-01T00:00:00Z",
}

# Stats come from API in camelCase (webhook stats endpoint doesn't use format layer)
SAMPLE_STATS_RAW = {
    "total": 100,
    "success": 95,
    "failed": 5,
    "successRate": 0.95,
    "byEventType": [
        {"eventType": "call_started", "total": 50, "success": 48, "failed": 2},
    ],
    "byHour": [
        {"hour": "2026-01-01T00:00:00Z", "total": 10, "success": 9, "failed": 1},
    ],
}
