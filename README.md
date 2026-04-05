# saperly

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

## Docs

Full documentation: https://saperly.com/docs
