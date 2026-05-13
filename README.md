# saperly

> **Published at [github.com/Saperly/saperly-python](https://github.com/Saperly/saperly-python).** This copy in the monorepo is the development source.

Python SDK for [Saperly](https://saperly.com) — the phone carrier for AI agents. Requires Python 3.9+.

## Install

```bash
pip install saperly
```

## Quick Start

```python
from saperly import SaperlyClient

client = SaperlyClient(api_key="sk_live_...")

# Create a phone line
line = client.lines.create(
    name="Support",
    mode="webhook",
    webhook_url="https://myapp.com/webhook",
)
print(line.phone_number)  # +14155550123

# Make an outbound call (requires consent)
client.consent.grant(
    line_id=line.id,
    phone_number="+14155559999",
    consent_type="explicit_outbound",
    source="user_opted_in",
)
call = client.calls.create(
    line_id=line.id,
    to_number="+14155559999",
)
```

> Sign up first at https://saperly.com/login (magic-link) and mint an API key in the portal — there is no programmatic signup endpoint.

`mode` is `"webhook" | "audio" | "hosted"`. The REST API accepts the legacy alias `"text"` (coerced to `"webhook"`) for back-compat; new code should use `"webhook"` directly.

## Async

```bash
pip install saperly[async]
```

```python
from saperly import AsyncSaperlyClient

async with AsyncSaperlyClient(api_key="sk_live_...") as client:
    line = await client.lines.create(
        name="Support",
        mode="webhook",
        webhook_url="https://myapp.com/webhook",
    )
```

## Service keys + child API keys (v0.5.7.0)

A **service key** is a portal-minted root credential whose only job is to
mint **child API keys** programmatically via `POST /v1/keys`. Use this
pattern when an AI agent provisions its own key, scoped to a single line
with a monthly spend cap.

```python
from saperly import SaperlyClient

# Authenticated as a service key (sk_svc_...)
root = SaperlyClient(api_key="sk_svc_live_...")

# Mint a scoped child api key for a specific agent
child = root.keys.create(
    name="claude-prod-line-42",
    agent_label="claude-3-5-sonnet",
    line_id="line_...",
    permissions="call_only",
    monthly_cap_cents=5_000,
)
print(child.plaintext_key)  # sk_live_... — shown ONCE; store securely

# Read the unified audit feed scoped to the caller
audit = root.audit.list(limit=100)
```

Idempotency: every POST to `/v1/keys` (and other mutating endpoints) accepts an `Idempotency-Key` header. Pass it via the per-call options if you need replay safety.

## Resources

| Resource | Methods |
|----------|---------|
| `client.lines` | `create`, `list`, `get`, `update`, `delete`, `send_sms` |
| `client.calls` | `create`, `conversation` (hosted AI call: `topic`, `begin_message?`, `max_duration_seconds?`), `list`, `get`, `hangup` |
| `client.messages` | `send` (outbound SMS) |
| `client.conversations` | `list` (cursor pagination), `messages(line_id, phone_number)` |
| `client.consent` | `grant`, `check`, `revoke` |
| `client.compliance` | `audit` |
| `client.audit` | `list` (unified audit feed, v0.5.7.0+) |
| `client.disclosures` | `create`, `list` |
| `client.keys` | `create`, `list`, `get`, `update`, `rotate`, `delete` (service-key auth required) |
| `client.billing` | `balance`, `transactions` |
| `client.webhooks` | `deliveries`, `stats`, `test` |
| `client.usage` | `daily`, `monthly` |
| `client.settings` | `get`, `update` |
| `client.voices` | `list` |

## Automatic Retries

GET and DELETE requests automatically retry once on 5xx errors and network failures, with a 1-second delay. POST/PUT/PATCH requests are never retried to prevent duplicate side effects.

## SMS

Both directions are live. Your line receives incoming text messages and your
webhook gets `sms_received` events. Send outbound SMS via `client.messages.send()`
— requires either an inbound from the recipient within the last 24 hours OR
an active `explicit_outbound` consent record on file for that (line, recipient)
pair (recorded via `consent.grant` or a documented web-form opt-in).

## Verifying webhooks

Every Saperly webhook is signed. `verify_webhook(raw_body, secret, headers)` returns an object with `.valid` and `.reason`.

```python
from flask import Flask, request, jsonify
from saperly.webhooks_verify import verify_webhook

app = Flask(__name__)

@app.route("/saperly-webhook", methods=["POST"])
def webhook():
    raw_body = request.get_data(as_text=True)
    line_id = request.get_json(force=True)["line_id"]
    secret = lookup_secret_for_line(line_id)  # your secret store
    result = verify_webhook(raw_body, secret, dict(request.headers))
    if not result.valid:
        return jsonify({"error": result.reason}), 401

    event = request.get_json(force=True)
    # ... trusted, handle the event
    return "", 200
```

The helper enforces the 5-minute clock-skew window and uses `hmac.compare_digest` for constant-time compare. You still need to cache `x-saperly-delivery-id` for 5 minutes and reject duplicates yourself — that cache is receiver-side state.

## Migration

- **v0.5.7.0** — Agent-native key management. New `client.keys.*` + `client.audit.list()`. Service keys mint scoped child api keys via `POST /v1/keys`. See [v0.5.7.0 migration guide](https://docs.saperly.com/migrations/v0.5.7.0).
- **v0.5.x** — Cents-honest USD pricing (replaces the credits abstraction). `client.billing.balance()` returns USD cents.
- **v0.3.0.0** — See [v0.3.0.0 migration guide](https://docs.saperly.com/migrations/v0.3.0.0).

## Docs

Full documentation: https://docs.saperly.com
