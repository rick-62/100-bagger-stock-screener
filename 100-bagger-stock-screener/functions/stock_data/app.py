
import datetime as dt
from typing import List

import requests
from typeguard import typechecked

URL = "https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{}"
FIELDS = []


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

    get_yahoo_json_data(symbol, fields)

    # Best to store as JSON into one dymamo field - see code example in chat 
    # field flagging if issue with requests or reason for missing data
    # run through pydantic model to check value etc make sense
    # Any issues need to be logged
    # Dpendent on error, if requests issue then fail else try best to get into DB





