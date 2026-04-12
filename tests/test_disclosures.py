from __future__ import annotations

import responses

from saperly import Disclosure
from tests.conftest import BASE_URL, SAMPLE_DISCLOSURE


class TestDisclosures:
    def test_create_returns_disclosure(self, mock_api, client):
        mock_api.add(
            responses.POST,
            f"{BASE_URL}/api/v1/disclosures",
            json={"disclosure": SAMPLE_DISCLOSURE},
            status=201,
        )
        disclosure = client.disclosures.create(message="This call uses AI.")

        assert isinstance(disclosure, Disclosure)
        assert disclosure.id == "disc-1"
        assert disclosure.message == "This call uses AI."
        assert disclosure.language == "en"
        assert disclosure.jurisdiction == "us"
        assert disclosure.is_default is True
