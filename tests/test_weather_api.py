import pytest
import requests

from main import (
    get_daily_weather_data,
)


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


@pytest.fixture
def mock_requests(monkeypatch):
    def mock_get(*args, **kwargs):
        return MockResponse({"current": {"temperature": 20}}, 200)

    monkeypatch.setattr(requests, "get", mock_get)


def test_get_daily_weather_data(mock_requests):
    # Replace 'API_KEY', 'location', and 'formatted_date' with actual values
    result = get_daily_weather_data()
    assert "temperature" in result
    assert result["temperature"] == 20


def test_get_daily_weather_data_exception(mock_requests):
    def mock_get(*args, **kwargs):
        return MockResponse(None, 500)

    monkeypatch.setattr(requests, "get", mock_get)

    with pytest.raises(Exception):
        get_daily_weather_data()


if __name__ == "__main__":
    pytest.main()
