
import datetime as dt

from typing import List


URL = "https://query2.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}"


def calc_future_timestamp(days_from_now: int) -> int:
    """given a number of days from now, returns integer timestamp""" 

    dt_object = dt.datetime.now()
    dt_object += dt.timedelta(days=days_from_now)
    future_timestamp = int(dt_object.timestamp())

    return future_timestamp


def get_yahoo_json_data(fields: List[str]):
    """provided a list of desired fields, returns full JSON response from yahoo"""

    params = {
        'period1': 493590046,
        'period2': calc_future_timestamp(150),
        'type': ",".join(fields),
    }

    headers = {'user-agent': "Python Web Scraper"}

    response = requests.get(URL, params=params, headers=headers)
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
    pass

    # try to download key financial data from Yahoo
        # find exaclt how to download data and from which location
        # run through pydantic model
        # Any issues need to be logged
        # Dpendent on error, if requests issue then fail else try best to get into DB

    # Update DynamoDB table accordingly
    # and repeat until a defined limit (defined in OS environment?)





