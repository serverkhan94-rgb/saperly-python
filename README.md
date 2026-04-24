# saperly

> **Published at [github.com/Saperly/saperly-python](https://github.com/Saperly/saperly-python).** This copy in the monorepo is the development source.

Python SDK for [Saperly](https://saperly.com) — the phone carrier for AI agents.

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
    mode="text",
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

## Async

```bash
pip install saperly[async]
```

```python
from saperly import AsyncSaperlyClient

async with AsyncSaperlyClient(api_key="sk_live_...") as client:
    line = await client.lines.create(
        name="Support",
        mode="text",
        webhook_url="https://myapp.com/webhook",
    )
```

## Resources

| Resource | Methods |
|----------|---------|
| `client.lines` | `create`, `list`, `get`, `delete`, `send_sms` |
| `client.calls` | `create`, `list`, `get`, `hangup` |
| `client.consent` | `grant`, `check`, `revoke` |
| `client.compliance` | `audit` |
| `client.disclosures` | `create`, `list` |
| `client.billing` | `balance` |
| `client.webhooks` | `deliveries`, `stats`, `test` |

## Automatic Retries

GET and DELETE requests automatically retry once on 5xx errors and network failures, with a 1-second delay. POST/PUT/PATCH requests are never retried to prevent duplicate side effects.

## SMS

SMS is inbound only for MVP. Your line receives incoming text messages and your
webhook gets `sms_received` events. Outbound SMS coming soon.

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

Migrating from an earlier version? See [v0.3.0.0 migration guide](https://saperly.com/docs/migrations/v0.3.0.0).

## Docs

Full documentation: https://saperly.com/docs
