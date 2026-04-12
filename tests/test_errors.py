from __future__ import annotations

from saperly import ConsentRequiredError, SaperlyError, ValidationError


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
