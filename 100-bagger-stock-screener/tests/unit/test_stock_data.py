
import json
from unittest.mock import patch

import pytest
import requests
from freezegun import freeze_time
from functions.stock_data import app
from typeguard import TypeCheckError
from unittest import result


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


@pytest.mark.parametrize("value, result", [
    ([1,0,-1], 0),
    ([1,2,0], 0),
    ([10,20,50], 0),
    ([5,10,40], 3),
    ([0,2,1], 10),
    ([0,5,10], 10),
    ([10,20,60], 0),
])
def test_score_pe(value, result):
    score_card = app.Score
    score_card.data['trailingPeRatio'] = value
    assert score_card.score_pe() == result


@pytest.mark.parametrize("value, result", [
    ([0,0,-1], 0),
    ([-1,3,0], 0),
    ([30,40,50], 0),
    ([10,20,40], 0),
    ([0,0,1], 10),
    ([3,4,10], 0),
    ([1,2,4], 9),
    ([1,4,6], 7)
])
def test_score_pb(value, result):
    score_card = app.Score
    score_card.data['trailingPbRatio'] = value
    assert score_card.score_pb() == result


@pytest.mark.parametrize("value, result", [
    ([0,0,0], 0),
    ([0,0,-1], 0),
    ([-1,-2,3], 10),
    ([-1,-2,-0.5], 5),
    ([0,0,1], 10),
    ([10,20,5], 5),
    ([2], 5),
])
def test_score_freecashflow(value, result):
    score_card = app.Score
    score_card.data['annualFreeCashFlow'] = value
    assert score_card.score_freecashflow() == result



@pytest.mark.parametrize("value, result", [
    ([0,0,0], 0),       # no growth
    ([1,2,3], 3),       # fast growth
    ([1,1.2,1.5], 5),   # steady growth
    ([5,6,7],  5),      # steady growth
    ([7,6,5], 0),       # negative growth
    ([7,5,7], 0),       # no growth
    ([1], 0),           # no date/growth
    ([9,12], 5),        # steady growth    
])
def test_score_revenue_profit_growth(value, result):
    score_card = app.Score
    score_card.data['annualTotalRevenue'] = value
    score_card.data['annualNetIncome'] = value
    assert score_card.score_revenue_profit_growth('profit') == result
    assert score_card.score_revenue_profit_growth('revenue') == result





 

