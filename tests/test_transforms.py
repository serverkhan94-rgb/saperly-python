from __future__ import annotations

from saperly._transforms import to_snake_keys


class TestToSnakeKeys:
    def test_single_word(self):
        assert to_snake_keys({"hello": 1}) == {"hello": 1}

    def test_camel_to_snake(self):
        raw = {
            "successRate": 0.95,
            "byEventType": [
                {"eventType": "call_started", "total": 50},
            ],
        }
        expected = {
            "success_rate": 0.95,
            "by_event_type": [
                {"event_type": "call_started", "total": 50},
            ],
        }
        assert to_snake_keys(raw) == expected

    def test_nested_transform(self):
        raw = {
            "topLevel": {
                "innerKey": [
                    {"deepKey": "value"},
                ],
            },
        }
        expected = {
            "top_level": {
                "inner_key": [
                    {"deep_key": "value"},
                ],
            },
        }
        assert to_snake_keys(raw) == expected

    def test_already_snake(self):
        data = {"line_id": "x", "phone_number": "y"}
        assert to_snake_keys(data) == data

    def test_acronyms(self):
        raw = {"callSID": "abc", "HTTPStatus": 200, "ttsURL": "https://x"}
        expected = {"call_sid": "abc", "http_status": 200, "tts_url": "https://x"}
        assert to_snake_keys(raw) == expected
