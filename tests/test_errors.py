from __future__ import annotations

from saperly import (
    AgentCapExceededError,
    AgentPermissionDeniedError,
    AgentScopeError,
    ConsentRequiredError,
    M3FraudBlockError,
    SaperlyError,
    ValidationError,
)


class TestErrorMapping:
    def test_maps_validation_error_with_details(self):
        body = {
            "error": {
                "code": "validation_error",
                "message": "Invalid input",
                "details": [
                    {"message": "name is required", "field": "name"},
                    {"message": "mode must be text or audio", "field": "mode"},
                ],
            },
        }
        err = SaperlyError.from_response(422, body)
        assert isinstance(err, ValidationError)
        assert err.code == "validation_error"
        assert err.status == 422
        assert len(err.details) == 2
        assert err.details[0].field == "name"
        assert err.details[1].message == "mode must be text or audio"

    def test_maps_consent_required(self):
        body = {
            "error": {
                "code": "consent_required",
                "message": "Consent required before calling this number",
            },
        }
        err = SaperlyError.from_response(403, body)
        assert isinstance(err, ConsentRequiredError)
        assert err.code == "consent_required"
        assert err.status == 403

    def test_unknown_code_returns_base(self):
        body = {
            "error": {
                "code": "some_future_error",
                "message": "Something went wrong",
            },
        }
        err = SaperlyError.from_response(500, body)
        assert type(err) is SaperlyError
        assert err.code == "some_future_error"

    def test_none_body(self):
        err = SaperlyError.from_response(500, None)
        assert type(err) is SaperlyError
        assert err.code == "unknown"
        assert err.status == 500

    def test_agent_scope_error_from_response_with_details(self):
        body = {
            "error": {
                "code": "agent_scope_error",
                "message": "This key is scoped to a different line.",
                "details": [
                    {"field": "line_id", "message": "line-abc"},
                ],
            },
        }
        err = SaperlyError.from_response(403, body)
        assert isinstance(err, AgentScopeError)
        assert err.code == "agent_scope_error"
        assert err.status == 403
        assert len(err.details) == 1
        assert err.details[0].field == "line_id"
        assert err.details[0].message == "line-abc"

    def test_agent_cap_exceeded_from_response_with_details(self):
        body = {
            "error": {
                "code": "agent_cap_exceeded",
                "message": "Monthly cap reached ($10.00).",
                "details": [
                    {"field": "spent_cents", "message": "1000"},
                    {"field": "cap_cents", "message": "1000"},
                    {
                        "field": "cycle_reset_at",
                        "message": "2026-06-01T00:00:00.000Z",
                    },
                ],
            },
        }
        err = SaperlyError.from_response(402, body)
        assert isinstance(err, AgentCapExceededError)
        assert err.code == "agent_cap_exceeded"
        assert err.status == 402
        assert len(err.details) == 3
        assert err.details[0].field == "spent_cents"
        assert err.details[0].message == "1000"
        assert err.details[1].field == "cap_cents"
        assert err.details[2].field == "cycle_reset_at"

    def test_agent_permission_denied_from_response_with_details(self):
        body = {
            "error": {
                "code": "agent_permission_denied",
                "message": "This key cannot perform this action.",
                "details": [
                    {"field": "permissions", "message": "tier=read_only verb=call"},
                ],
            },
        }
        err = SaperlyError.from_response(403, body)
        assert isinstance(err, AgentPermissionDeniedError)
        assert err.code == "agent_permission_denied"
        assert err.status == 403
        assert len(err.details) == 1
        assert err.details[0].field == "permissions"
        assert err.details[0].message == "tier=read_only verb=call"

    def test_m3_fraud_block_from_response_no_details(self):
        body = {
            "error": {
                "code": "m3_fraud_block",
                "message": "Request blocked by abuse protection.",
            },
        }
        err = SaperlyError.from_response(403, body)
        assert isinstance(err, M3FraudBlockError)
        assert err.code == "m3_fraud_block"
        assert err.status == 403
        assert err.details == []
