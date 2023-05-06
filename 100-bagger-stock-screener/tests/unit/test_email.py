import pytest

from functions.stock_email import app


@pytest.fixture
def event_data():
    return [
        {
            "ISIN": "US0378331005",
            "total_score": 15,
            "timestamp": "2022-12-14T16:51:23.123456"
        },
        {
            "ISIN": "US5949181045",
            "total_score": 6,
            "timestamp": "2022-12-14T17:01:23.123456"
        },
    ]

def test_create_email_body(event_data):
    output = app.create_email_body(event_data)
    assert "ISIN:" in output
    assert "US0378331005" in output
    assert "2022-12-14T17:01:23.123456" in output
    assert "6" in output
    assert "15" in output