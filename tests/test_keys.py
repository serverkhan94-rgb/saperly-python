from __future__ import annotations

import json

import httpx
import pytest
import responses
import respx

from saperly import (
    AgentCapExceededError,
    AgentPermissionDeniedError,
    AgentScopeError,
    ApiKey,
    ApiKeyListResult,
    AsyncSaperlyClient,
    CreateApiKeyResponse,
    IdempotencyKeyReusedError,
    RateLimitedError,
)
from tests.conftest import BASE_URL

SAMPLE_KEY_WIRE = {
    "id": "key_1",
    "key_prefix": "sk_live_abc",
    "environment": "live",
    "name": "support-bot",
    "agent_label": "agent-1",
    "line_id": "line_1",
    "permissions": "call_only",
    "monthly_cap_cents": 5000,
    "monthly_spend_cents": 230,
    "created_at": "2026-05-12T00:00:00Z",
    "revoked_at": None,
    "last_used_at": None,
    "rotated_from": None,
    "created_by_service_key_id": "key_parent",
}

SAMPLE_CREATE_WIRE = {
    **SAMPLE_KEY_WIRE,
    "plaintext_key": "sk_live_abcdef1234567890",
}


class TestKeysCreate:
    def test_sends_idempotency_header_and_body(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"key": SAMPLE_CREATE_WIRE},
            status=201,
        )
        result = client.keys.create(
            name="support-bot",
            agent_label="agent-1",
            line_id="line_1",
            permissions="call_only",
            monthly_cap_cents=5000,
        )
        assert isinstance(result, CreateApiKeyResponse)
        assert result.plaintext_key == "sk_live_abcdef1234567890"
        assert result.key_prefix == "sk_live_abc"
        assert result.permissions == "call_only"
        assert result.monthly_cap_cents == 5000

        req = mock_api.calls[0].request
        assert req.headers.get("Idempotency-Key")  # auto-generated UUID v4
        body = json.loads(req.body)
        assert body["name"] == "support-bot"
        assert body["agent_label"] == "agent-1"
        assert body["line_id"] == "line_1"
        assert body["permissions"] == "call_only"
        assert body["monthly_cap_cents"] == 5000

    def test_uses_caller_supplied_idempotency_key(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"key": SAMPLE_CREATE_WIRE},
            status=201,
        )
        client.keys.create(name="x", idempotency_key="my-custom-key")
        assert mock_api.calls[0].request.headers["Idempotency-Key"] == "my-custom-key"

    def test_omits_optional_fields_when_not_passed(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"key": SAMPLE_CREATE_WIRE},
            status=201,
        )
        client.keys.create(name="x")
        body = json.loads(mock_api.calls[0].request.body)
        assert body == {"name": "x", "permissions": "full"}

    def test_raises_agent_scope_error(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"error": {"code": "agent_scope_error", "message": "line scope"}},
            status=403,
        )
        with pytest.raises(AgentScopeError):
            client.keys.create(name="x")

    def test_raises_agent_cap_exceeded(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"error": {"code": "agent_cap_exceeded", "message": "cap reached"}},
            status=402,
        )
        with pytest.raises(AgentCapExceededError):
            client.keys.create(name="x")

    def test_raises_agent_permission_denied(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"error": {"code": "agent_permission_denied", "message": "denied"}},
            status=403,
        )
        with pytest.raises(AgentPermissionDeniedError):
            client.keys.create(name="x")

    def test_raises_idempotency_key_reused(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"error": {"code": "idempotency_key_reused", "message": "reused"}},
            status=409,
        )
        with pytest.raises(IdempotencyKeyReusedError):
            client.keys.create(name="x", idempotency_key="dup")

    def test_raises_rate_limited(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"error": {"code": "rate_limited", "message": "slow down"}},
            status=429,
        )
        with pytest.raises(RateLimitedError):
            client.keys.create(name="x")


class TestKeysList:
    def test_sends_pagination_and_returns_result(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/keys",
            json={"keys": [SAMPLE_KEY_WIRE], "total": 1},
            status=200,
        )
        result = client.keys.list(limit=25, offset=50)
        assert isinstance(result, ApiKeyListResult)
        assert result.total == 1
        assert len(result.keys) == 1
        assert isinstance(result.keys[0], ApiKey)
        assert result.keys[0].id == "key_1"
        assert "limit=25" in mock_api.calls[0].request.url
        assert "offset=50" in mock_api.calls[0].request.url


class TestKeysGet:
    def test_returns_apikey_from_envelope(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/keys/key_1",
            json={"key": SAMPLE_KEY_WIRE},
            status=200,
        )
        result = client.keys.get("key_1")
        assert isinstance(result, ApiKey)
        assert result.id == "key_1"
        assert result.permissions == "call_only"


class TestKeysUpdate:
    def test_sends_only_provided_fields(self, mock_api, client):
        updated = {**SAMPLE_KEY_WIRE, "name": "renamed"}
        mock_api.add(
            responses.PATCH,
            f"{BASE_URL}/api/v1/keys/key_1",
            json={"key": updated},
            status=200,
        )
        result = client.keys.update("key_1", name="renamed")
        assert isinstance(result, ApiKey)
        assert result.name == "renamed"
        body = json.loads(mock_api.calls[0].request.body)
        assert body == {"name": "renamed"}

    def test_forwards_explicit_none_to_clear_field(self, mock_api, client):
        cleared = {**SAMPLE_KEY_WIRE, "agent_label": None}
        mock_api.add(
            responses.PATCH,
            f"{BASE_URL}/api/v1/keys/key_1",
            json={"key": cleared},
            status=200,
        )
        client.keys.update("key_1", agent_label=None)
        body = json.loads(mock_api.calls[0].request.body)
        assert body == {"agent_label": None}

    def test_omits_field_when_not_provided(self, mock_api, client):
        mock_api.add(
            responses.PATCH,
            f"{BASE_URL}/api/v1/keys/key_1",
            json={"key": SAMPLE_KEY_WIRE},
            status=200,
        )
        client.keys.update("key_1", name="x")
        body = json.loads(mock_api.calls[0].request.body)
        assert "agent_label" not in body
        assert "line_id" not in body
        assert "monthly_cap_cents" not in body


class TestKeysDelete:
    def test_returns_revoked_apikey(self, mock_api, client):
        revoked = {**SAMPLE_KEY_WIRE, "revoked_at": "2026-05-12T01:00:00Z"}
        mock_api.add(
            responses.DELETE,
            f"{BASE_URL}/api/v1/keys/key_1",
            json={"key": revoked},
            status=200,
        )
        result = client.keys.delete("key_1")
        assert isinstance(result, ApiKey)
        assert result.revoked_at == "2026-05-12T01:00:00Z"


class TestKeysRotate:
    def test_sends_idempotency_header_returns_plaintext(self, mock_api, client):
        rotated_wire = {
            **SAMPLE_CREATE_WIRE,
            "id": "key_2",
            "rotated_from": "key_1",
            "plaintext_key": "sk_live_newrotated",
        }
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys/key_1/rotate",
            json={"key": rotated_wire},
            status=201,
        )
        result = client.keys.rotate("key_1")
        assert isinstance(result, CreateApiKeyResponse)
        assert result.plaintext_key == "sk_live_newrotated"
        assert result.rotated_from == "key_1"
        assert mock_api.calls[0].request.headers.get("Idempotency-Key")


class TestAsyncKeys:
    @respx.mock
    async def test_create_async(self):
        route = respx.post(f"{BASE_URL}/api/v1/keys").mock(
            return_value=httpx.Response(201, json={"key": SAMPLE_CREATE_WIRE}),
        )
        client = AsyncSaperlyClient(api_key="sk_test", base_url=BASE_URL)
        result = await client.keys.create(name="support-bot")
        assert route.called
        assert isinstance(result, CreateApiKeyResponse)
        assert result.plaintext_key == "sk_live_abcdef1234567890"
        assert route.calls[0].request.headers.get("Idempotency-Key")
        await client.aclose()

    @respx.mock
    async def test_get_async(self):
        route = respx.get(f"{BASE_URL}/api/v1/keys/key_1").mock(
            return_value=httpx.Response(200, json={"key": SAMPLE_KEY_WIRE}),
        )
        client = AsyncSaperlyClient(api_key="sk_test", base_url=BASE_URL)
        result = await client.keys.get("key_1")
        assert route.called
        assert isinstance(result, ApiKey)
        assert result.id == "key_1"
        await client.aclose()


# /review hardening (2026-05-12): coverage for paths the original suite
# missed. Each test is paired with a fingerprint to the specialist finding
# it closes.


class TestKeysPathEncoding:
    """Path-traversal defense: key ids are URL-encoded by resources/keys.py
    via urllib.parse.quote(key_id, safe=''). TS tests path traversal in
    keys.test.ts:240; Python parity is added here.
    """

    def test_get_encodes_path_traversal_chars(self, mock_api, client):
        encoded_url = f"{BASE_URL}/api/v1/keys/a%2Fb%2F..%2Fc"
        mock_api.add(
            responses.GET,
            encoded_url,
            json={"key": SAMPLE_KEY_WIRE},
            status=200,
        )
        client.keys.get("a/b/../c")
        url = mock_api.calls[0].request.url
        assert "%2F" in url
        assert "%2E%2E" in url or "/.." not in url.split("/api/v1/keys/")[-1]


class TestKeysIdempotencyReplay:
    """Server redacts plaintext_key on idempotency replay (route.ts:177-207).
    The Python dataclass declares plaintext_key as Optional[str]; this pins
    the SDK contract so a regression that re-types it as required would
    fail here.
    """

    def test_create_handles_redacted_replay(self, mock_api, client):
        replay_wire = {**SAMPLE_KEY_WIRE}  # no plaintext_key
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/keys",
            json={"key": replay_wire},
            status=201,
        )
        result = client.keys.create(name="agent", idempotency_key="replayed")
        assert result.plaintext_key is None
        assert result.id == "key_1"
        assert result.key_prefix == "sk_live_abc"
