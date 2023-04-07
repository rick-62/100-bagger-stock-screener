
## IN PROGRESS ##


def get_yahoo_json_data():
    # within session
    pass



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





