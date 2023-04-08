
from unittest.mock import patch

import pytest
import requests
from freezegun import freeze_time
from functions.stock_data import app
from typeguard import TypeCheckError


@freeze_time("2022-01-01")  # timestamp:1640995200
def test_calc_future_timestamp():
    secs_in_a_day = 86400
    timestamp = 1640995200

    # exact match
    assert app.calc_future_timestamp(1) == timestamp + secs_in_a_day
    assert app.calc_future_timestamp(100) == timestamp + 100 * secs_in_a_day
    assert app.calc_future_timestamp(1000) == timestamp + 1000 * secs_in_a_day
    assert app.calc_future_timestamp(0) == timestamp

    # failed match 
    assert app.calc_future_timestamp(0) != 1640995201
    assert app.calc_future_timestamp(1000) != 1640995201 + 100 * secs_in_a_day


@patch('requests.get')
def test_get_yahoo_json_data(mock_get):
    mock_response = {'key': 'value'}
    mock_get.return_value.json.return_value = mock_response

    assert app.get_yahoo_json_data('AAPL', ['annualMarketCap']) == mock_response

    with pytest.raises(TypeCheckError):
        app.get_yahoo_json_data('AAPL', 'annualMarketCap')
        app.get_yahoo_json_data(888, ['annualMarketCap'])


