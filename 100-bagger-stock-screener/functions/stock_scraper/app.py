import os
import random

import pandas as pd
import pydantic

from pydantic import BaseModel, Field
from typing import List, Dict


class ISINFormatError(Exception):
    """Custom error which is raised when the ISIN doesn't have the correct format"""

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
        """checks the ISIN is correct, raising ISINFormatError otherwise"""

        def checksum(value):
            converted_alpha = "".join([
                v if v.isdigit() else str(ord(v) - 55)
                for v in value[:-1]
            ])
            check_digit = int(value[-1])
            digits = [int(d) for d in converted_alpha[::-1]]
            checksum = 0
            for d in digits[::2]:
                checksum += sum([int(x) for x in str(2 * d)])
            checksum += sum(digits[1::2])
            return (checksum + check_digit) % 10 == 0

        if value == "":
            raise ISINFormatError(value=value, message="ISIN is missing.")

        if not value[-1].isdigit():
            raise ISINFormatError(value=value, message="ISIN checksum digit incorrect.")

        if not checksum(value):
            raise ISINFormatError(value=value, message="ISIN checksum failure.")

        return value


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
        try:
            model = FreetradeModel(**record)
        except ISINFormatError:
            


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


    





