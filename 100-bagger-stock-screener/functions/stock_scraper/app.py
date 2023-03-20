import os
import random

import pandas as pd
import pydantic

from pydantic import BaseModel, Field
from typing import List, Dict



class ISINFormatError(Exception):
    """Customs error which is raised when the ISIN doesn't have the correct format"""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)



class FreetradeModel(BaseModel):
    title: str = Field(..., alias="Title")
    long_title: str = Field(..., alias="Long_Title")
    subtitle: str = Field(..., alias="Subtitle")
    currency: str = Field(..., alias="Currency")
    isa_eligible: bool = Field(..., alias="ISA_eligible")
    isin: str = Field(..., alias="ISIN")
    mic: str = Field(..., alias="MIC")
    symbol: str = Field(..., alias="Symbol")
    fractional_enabled: bool = Field(..., alias="Fractional_Enabled")


    @pydantic.validator("isin")
    @classmethod
    def isin_valid(cls, value):
        raise ISINFormatError(
            value=value, 
            message="ISIN does not meet the required format."
        )
        return value

def luhn_algo(num):
    digits = [int(d) for d in str(num)]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum([int(x) for x in str(2 * d)])
    return checksum % 10 == 0

def get_stock_list() -> List[Dict]:
    """Downloads stock list from Freetrade Google Sheet, and returns as dictionary"""

    return (
        pd
        .read_csv(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv")
        .to_dict(orient='records')
    )


def lambda_handler(event, context):

    LIMIT = 5
    SHEET_ID = "14Ep-CmoqWxrMU8HshxthRcdRW8IsXvh3n2-ZHVCzqzQ"

    stock_list = get_stock_list()

    random.shuffle(stock_list)

    count = 0
    for record in stock_list:
        

        # check data satifies pydantic data model
            # if does not then skip e.g. ETF or missing key data
            # log any issues
            # else continue
        model = FreetradeModel(**record)
        print(model)


        count += 1
        if count > 4:
            break

        # check if stock already exists in dynamoDB
            # if does then skip
            # else continue
    


    # try to download key financial data from Yahoo
        # run through pydantic model & log issues
        # Any issues need to be logged
        # Errors here will not be skipped

    # Update DynamoDB table accordingly
    # and repeat until a defined limit (defined in OS environment?)


    





