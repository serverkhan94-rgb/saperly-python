from __future__ import annotations

import pytest
import responses

from saperly import ConsentAlreadyGrantedError, ConsentCheckResult, ConsentRecord
from tests.conftest import BASE_URL, SAMPLE_CONSENT


class TestConsent:
    def test_grant_duplicate_raises(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/consent",
            json={
                "error": {
                    "code": "consent_already_granted",
                    "message": "Consent already exists for this phone number and line",
                },
            },
            status=409,
        )
        with pytest.raises(ConsentAlreadyGrantedError) as exc_info:
            client.consent.grant(
                line_id="line-1",
                phone_number="+14155559999",
                consent_type="explicit_outbound",
                source="api",
            )
        assert exc_info.value.code == "consent_already_granted"
        assert exc_info.value.status == 409

    def test_check_returns_nested(self, mock_api, client):
        mock_api.add(
            responses.GET,
            f"{BASE_URL}/api/v1/consent",
            json={"status": "active", "consent": SAMPLE_CONSENT},
            status=200,
        )
        result = client.consent.check(phone_number="+14155559999", line_id="line-1")

        assert isinstance(result, ConsentCheckResult)
        assert result.status == "active"
        assert isinstance(result.consent, ConsentRecord)
        assert result.consent.id == "consent-1"
        assert result.consent.phone_number == "+14155559999"
        assert result.consent.consent_type == "explicit_outbound"
