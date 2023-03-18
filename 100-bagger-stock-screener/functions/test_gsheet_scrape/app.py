import os

import pandas as pd

from pydantic import BaseModel


# create pydantic model(s) for google sheet and Yahoo data

class FreetradeStock(BaseModel):
    title: str
    long_title: str
    subtitle: str
    currency: str
    isa_eligible: bool
    isin: str
    mic: str
    symbol: str
    fractional_enabled: bool


# import data from google sheets
sheet_id = "14Ep-CmoqWxrMU8HshxthRcdRW8IsXvh3n2-ZHVCzqzQ"  # OS environment

df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv")

print(df.head())

# randomly select a record from dataframe

idx = df.index.to_list()
shuffle(idx)

count = 5
while count:
    i = idx.pop()
    print(df.loc[i, 'Title'])

    # check if stock already exists in dynamoDB
        # if does then skip
        # else continue

    count -= 1

    

    # check data satifies pydantic data model
        # if does not then skip e.g. ETF or missing key data
        # log any issues
        # else continue

    # try to download key financial data from Yahoo
        # run through pydantic model & log issues
        # Any issues need to be logged
        # Errors here will not be skipped

    # Update DynamoDB table accordingly
    # and repeat until a defined limit (defined in OS environment?)


    





