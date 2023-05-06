
import datetime as dt
import json
from typing import List, Dict

import requests
from typeguard import typechecked

URL = "https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{}"
FIELDS = [
    "trailingMarketCap",
    "trailingPeRatio",
    "trailingPbRatio",
    "annualFreeCashFlow",
    "annualTotalRevenue",
    "annualNetIncome",
]


def calc_future_timestamp(days_from_now: int) -> int:
    """given a number of days from now, returns integer timestamp""" 

    dt_object = dt.datetime.now()
    dt_object += dt.timedelta(days=days_from_now)
    future_timestamp = int(dt_object.timestamp())

    return future_timestamp


@typechecked
def get_yahoo_json_data(symbol: str, fields: List[str]):
    """provided stock symbol & list of desired fields, returns full JSON response from yahoo"""

    params = {
        'period1': 493590046,
        'period2': calc_future_timestamp(150),
        'type': ",".join(fields),
    }

    headers = {'user-agent': "Python Web Scraper"}

    response = requests.get(URL.format(symbol), params=params, headers=headers)
    response.raise_for_status()

    return response.json()


class Score:
    """Object for calculating scores based on stock fundamentals"""

    data: Dict = {} 

    @classmethod
    def __init__(cls, json_response: json):
        cls.data = cls.transform_input(json_response)

    @classmethod
    def transform_input(cls, json_response: json):
        """transform yahoo json response to simplified lookup dict"""
        data = {}
        for result in json_response['timeseries']['result']:
            field_name = result['meta']['type'][0]
            data[field_name] = [point['reportedValue']['raw'] for point in result[field_name]]
        return data


    @classmethod
    def score_market_cap(cls):
        """Calculate a score based on market cap amount"""
        market_cap = cls.data['trailingMarketCap'][0]

        # lower bound
        if market_cap < 500E6:
            return 100

        # upper bound
        elif market_cap >= 50E9:
            return 0

        # Gradient
        else:
            return int(100*(1-(market_cap/50E9))**3)

    
    @classmethod
    def score_pe(cls):
        """Calculate score based on recent P/E ratio"""
        pe = cls.data['trailingPeRatio'][-1]

        # lower bound
        if pe <= 0:
            return 0

        # upper bound
        elif pe > 50:
            return 0

        # Gradient
        else:
            return int(11*(1-(pe/50)**2))


    @classmethod
    def score_pb(cls):
        """Calculate score based on recent P/B ratio"""
        pb = cls.data['trailingPbRatio'][-1]

        # lower bound
        if pb <= 0:
            return 0

        # upper bound
        elif pb > 10:
            return 0

        # Gradient
        else:
            return int(11*(1-(pb/10)**2))

    
    @classmethod
    def score_freecashflow(cls):
        """Calculate score based on recent free cash flow"""
        fcf = cls.data['annualFreeCashFlow']

        score = (

            # growth
            5 * (fcf[-1] > fcf[0]) + 

            # positive
            5 * (fcf[-1] > 0)
            
        )

        return score


    @classmethod
    def score_revenue_profit_growth(cls, measure: str):
        """
        Calculate score based on recent revenue & profit growth.
        measure is either 'revenue' or 'profit'.
        """

        field = 'annualNetIncome' if measure == "profit" else "annualTotalRevenue"
                    
        v1 = cls.data[field][0]
        v2 = cls.data[field][-1]

        try:
            growth_rate = (v2 - v1) / v1
            avg_growth_rate = growth_rate / (len(cls.data[field]) - 1)
        except ZeroDivisionError:
            return 0

        # steady growth
        if 0.1 < avg_growth_rate < 0.5:
            return 5

        # no growth
        if avg_growth_rate <= 0:
            return 0

        # slow or fast growth
        else:
            return 3


    @classmethod
    def get_total_score(cls):
        """Calculate total score for a given stock"""
        return (
            cls.score_market_cap() +
            cls.score_pe() +
            cls.score_pb() +
            cls.score_freecashflow() +
            cls.score_revenue_profit_growth("profit") +
            cls.score_revenue_profit_growth("revenue")
        )
     

def lambda_handler(event, context):
    """Lambda function which downloads Yahoo JSON data for a provided stock, and 
    calculated a simple score to prioritise. 

    Downloads key JSON data from Yahoo:
    - Market Capitalisation
    - PE/PB ratios
    - Free Cash Flow
    - Total Revenu
    - Net Income
  
    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function, providing stock data

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        dict: stock symbol, score & timestamp provided in form stock:dict[attribute:value]
    """
    
    json_response = get_yahoo_json_data(event["yahoo_symbol"], fields=FIELDS)

    score_card = Score(json_response)

    return {
        "ISIN": event["isin"],
        "total_score": score_card.get_total_score(),
        "timestamp": dt.datetime.now().isoformat()
    }


if __name__ == "__main__":
    print(lambda_handler({"yahoo_symbol": "AAPL"}, None))



