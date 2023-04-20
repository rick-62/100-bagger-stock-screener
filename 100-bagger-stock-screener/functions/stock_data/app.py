
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

    def __init__(self, json_response: json):
        self.data = self.transform_input(json_response)


    def transform_input(self, json_response: json):
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

    





    



def lambda_handler(event, context):
    """Lambda function which downloads Yahoo JSON data for a provided stock,
    and returning original data, plus additional. 

    Downloads key JSON data from Yahoo:
    - blah
    - blah
    - blah

    Additionally, creates new data:
    - scores?
    - amounts?
    - values?
  
    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function, providing stock data

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        dict: stock data provided in form stock:dict[attribute:value]
    """
    
    symbol = event["yahoo_symbol"]

    response = get_yahoo_json_data(symbol, fields=FIELDS)

    # need to figure out how to store in DynamoDB

    # Best to store as JSON into one dymamo field - see code example in chat 
    # field flagging if issue with requests or reason for missing data
    # run through pydantic model to check value etc make sense
    # Any issues need to be logged
    # Dpendent on error, if requests issue then fail else try best to get into DB





