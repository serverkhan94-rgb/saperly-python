# AGENTS.md: saperly (Python)

Patterns and pitfalls for AI coding agents (Claude Code, Cursor, Codex, OpenClaw) integrating the Saperly Python SDK. If you are an AI agent reading this autonomously, the canonical patterns below are tested and current as of v0.3.0.

## 1. What Saperly is

Saperly is the phone carrier for AI agents. One API call gives any agent a real phone number with TCPA compliance, consent capture, and an audit trail built in. Hosted mode runs the AI for you (Saperly handles speech-to-text, the LLM call, and text-to-speech). Webhook mode lets your backend decide responses turn by turn. Audio mode streams raw audio over a WebSocket if you need full control of the media plane.

## 2. Installation

```bash
pip install saperly
```

```python
import os
from saperly import SaperlyClient

saperly = SaperlyClient(api_key=os.environ["SAPERLY_API_KEY"])
```

Requires Python 3.9+. The sync client uses `requests`. For async, install `pip install "saperly[async]"` and import `AsyncSaperlyClient` (depends on `httpx`).

## 3. Authentication

Saperly uses a two-tier credential model. Both authenticate via `Authorization: Bearer <key>` on the wire; the prefix tells the auth dispatcher which tier you're on.

| Credential | Prefix | What it does | Where to get it |
| --- | --- | --- | --- |
| API key | `sk_test_…` / `sk_live_…` | Place calls, send SMS, manage lines, query usage, read `/v1/audit`. | Portal, or minted by a service key via `POST /v1/keys`. |
| Service key | `sk_svc_test_…` / `sk_svc_live_…` | Mint, list, get, update, rotate, revoke child API keys. Credential management only. | Portal only (Settings → Service Keys). |

Child API keys minted by a service key carry their own scope. The API accepts exactly four permission tiers on `POST /v1/keys` and `PATCH /v1/keys/{id}`. A fifth value, `legacy_full`, appears on responses for keys minted before v0.5.7.0 but cannot be set via the API.

| Permission | Settable | Returned | What it does |
| --- | --- | --- | --- |
| `full` | yes | yes | All call, SMS, line, and account operations. |
| `call_only` | yes | yes | Place and inspect calls; no SMS, no line mutation. |
| `sms_only` | yes | yes | Send and inspect SMS; no calls, no line mutation. |
| `read_only` | yes | yes | GETs only; no mutations. |
| `legacy_full` | no | yes | Backfill marker for keys minted before v0.5.7.0. |

Service keys cannot mint other service keys via API. The bootstrap step is portal-only by design (Stripe restricted-keys pattern). If you lose every service key, recover via the portal.

## 4. Core resources

- `lines`: Provision and manage phone numbers (hosted, webhook, or audio mode).
- `calls`: Place and monitor outbound calls, run hosted conversation calls.
- `messages`: Send and receive SMS, list conversations.
- `keys`: Mint, rotate, revoke child API keys (service key only).
- `consent`: Record explicit caller consent for TCPA compliance.
- `disclosures`: Configure inbound disclosure scripts.
- `webhooks`: Track event delivery; verify via signed HMAC-SHA256.
- `audit`: Read the immutable compliance event stream.

## 5. Canonical patterns

### Provision a hosted line

```python
import os
from saperly import SaperlyClient

saperly = SaperlyClient(api_key=os.environ["SAPERLY_API_KEY"])

line = saperly.lines.create(
    name="my agent",
    mode="hosted",
    system_prompt="You are a helpful assistant.",
)

print(line.phone_number)
```

Reuse an existing line by name before provisioning a new one. Phone numbers cost $2.50/month each (first number free for 30 days).

### Place a test outbound call

```python
call = saperly.calls.create(
    line_id=line.id,
    to_number="+14155551234",  # your real E.164 number
)

print(call.id, call.status)
```

Ask the human operator for `to_number` before placing the call. Never call `+1 555-0100` through `+1 555-0199`; those are reserved test numbers that will never connect.

### Mint a child API key (service key auth)

```python
import os
from saperly import SaperlyClient

svc = SaperlyClient(api_key=os.environ["SAPERLY_SERVICE_KEY"])

child = svc.keys.create(
    name="voice-agent-prod",
    line_id="550e8400-e29b-41d4-a716-446655440000",
    permissions="call_only",
    monthly_cap_cents=500,
)

# First and only chance to read the plaintext. Save it now.
print(child.plaintext_key)
```

`plaintext_key` is returned once on create. Store it in your secrets manager immediately; the server never re-emits it. The client auto-generates a UUID v4 `Idempotency-Key` for `keys.create` and `keys.rotate`; pass your own via the `idempotency_key` keyword if you need cross-process retry safety.

### Rotate a service-minted key

```python
rotated = svc.keys.rotate(child.id)
print(rotated.plaintext_key)  # new plaintext, old is dead
```

Rotation is atomic: the old plaintext stops working the instant the response returns.

## 6. Required headers

- `Authorization: Bearer <key>`: always. The client sets this from the `api_key` constructor argument.
- `Idempotency-Key: <uuid>`: required on `POST /v1/keys` and `POST /v1/keys/{id}/rotate`. The client auto-generates a UUID v4 for these endpoints when you don't pass one; supply your own via the `idempotency_key` keyword for cross-process retry safety. Recommended on `POST /v1/calls` and `POST /v1/messages`.
- `Content-Type: application/json`: set by the client on every body-carrying request.

## 7. Common pitfalls

1. **The env var is `SAPERLY_API_KEY`.** Not `SAPERLY_KEY`, not `SAPERLY_TOKEN`. For credential management, use a separate `SAPERLY_SERVICE_KEY` env var so the two tiers never collide in the same process.
2. **Snake case everywhere on the Python side.** Use `system_prompt`, `line_id`, `to_number`, `monthly_cap_cents`. The SDK passes those through to the REST API as-is. Camel case (the TypeScript SDK style) will raise a `TypeError` at the function call.
3. **`plaintext_key` is returned once.** Access `child.plaintext_key` on the `keys.create` and `keys.rotate` responses, then persist it. There is no read-back endpoint, and the dataclass field will not be present on `keys.get`.
4. **Async client lives at `saperly.AsyncSaperlyClient`.** Not `saperly.Client.async_()`. Construct it inside an `async with` block so the underlying `httpx.AsyncClient` closes cleanly. Install with `pip install "saperly[async]"`.

## 8. Resources

- Docs: https://docs.saperly.com
- Quickstart: https://docs.saperly.com/quickstart
- Agent onboarding: https://docs.saperly.com/agent-onboarding
- Service keys: https://docs.saperly.com/service-keys
- API reference: https://docs.saperly.com/api-reference
- llms.txt: https://saperly.com/llms.txt
- Issues: https://github.com/Saperly/saperly-python/issues
- Source: https://github.com/Saperly/saperly-python
