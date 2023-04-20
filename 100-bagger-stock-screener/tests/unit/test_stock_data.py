
import json
from unittest.mock import patch

import pytest
import requests
from freezegun import freeze_time
from functions.stock_data import app
from typeguard import TypeCheckError


def load_params_from_json(json_path):
    with open(json_path) as f:
        return json.load(f)


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
        app.get_yahoo_json_data()


@pytest.fixture
def score_card():
    response = load_params_from_json('100-bagger-stock-screener/tests/assets/yahoo_response.json')
    return app.Score(response)


def test_transform_input(score_card):
    assert isinstance(score_card.data, dict)
    assert isinstance(score_card.data['trailingMarketCap'], list)
    assert isinstance(score_card.data['trailingPeRatio'], list)
    assert isinstance(score_card.data['trailingPbRatio'], list)
    assert isinstance(score_card.data['annualTotalRevenue'], list)
    assert isinstance(score_card.data['annualNetIncome'], list)
    assert isinstance(score_card.data['annualFreeCashFlow'], list)
    assert score_card.data['trailingMarketCap'] == [5E11]
    assert score_card.data['trailingPeRatio'] == [86.222]
    assert score_card.data['trailingPbRatio'] == [20]
    assert score_card.data['annualTotalRevenue'] == [2.55E9, 3.16E9, 5.02E10, 8.11E9]
    assert score_card.data['annualNetIncome'] == [-8.2E7, 5.9E7, 5.9E8, 1.3E9]
    assert score_card.data['annualFreeCashFlow'] == [10E8, 3E9, 4.5E9, 7.5E9]


@pytest.mark.parametrize("market_cap, result", [
    (0, 100),
    (499E6, 100),
    (1E9, 94),
    (10E9, 51),
    (50E9, 0),
    (51E9, 0),
    (5E11, 0)
])
def test_score_market_cap(market_cap, result):
    score_card = app.Score
    score_card.data['trailingMarketCap'] = [market_cap]
    assert score_card.score_market_cap() == result


def test_score_pe_pb():
    ...


def test_score_freecashflow():
    ...


def test_score_growth():
    ...



 

