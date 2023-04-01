import os
import random

import boto3
import pandas as pd
import pydantic

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union


LIMIT = 5
SHEET_ID = "14Ep-CmoqWxrMU8HshxthRcdRW8IsXvh3n2-ZHVCzqzQ"
REQUESTS_CACHE_TTL = 1800  # seconds
ISA_ELIGIBLE = True
MIC_REFERENCE = {
    "XLON": ".L",
    "XETR": ".DE",
    "XHEL": ".HE",
    "XLIS": ".LS",
    "XAMS": ".AS",
    "XBRU": ".BR",
    "XWBO": ".VI",
    "XSTO": ".ST",
}


class ISINFormatError(Exception):
    """Custom error which is raised when the ISIN doesn't have the correct format"""

    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class ISAEligibilityError(Exception):
    """Custom error which is raised when not ISA eligible"""

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
    yahoo_symbol: str = None


    @pydantic.validator("isa_eligible")
    @classmethod
    def isa_eligibility(cls, value):
        """Determines whether stock is valid based on ISA eligiblity"""

        if ISA_ELIGIBLE and not value:
            raise ISAEligibilityError(value=value, message="Requires ISA eligibility.")

        return value


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


    @pydantic.validator("yahoo_symbol", always=True)
    @classmethod
    def create_yahoo_symbol(cls, _, values):
        """
        Convert Freetrade stock symbol based on exchange (MIC),
        ensuring it is adjusted for scraping Yahoo:
        XNAS	No change	
        XNYS	No change
        PINK	No change
        XLON	suffix: .L	
        XETR	suffix: .DE     remove suffix: d
        XHEL	suffix: .HE	    remove suffix: h
        XLIS	suffix: .LS	    remove suffix: u
        XAMS	suffix: .AS	    remove suffix: a
        XBRU	suffix: .BR	    remove suffix: b
        XWBO	suffix: .VI     remove suffix: v
        XSTO	suffix: .ST or -A.ST or -B.ST
        """

        mic = values["mic"]
        symbol = values["symbol"]

        # Retain only uppercase letters, removing lowercase suffix and "."
        yh = "".join([i for i in symbol if not i.islower() and i != "."])

        # special case for XSTO
        if mic == "XSTO":
            if yh.endswith("A") or yh.endswith("B"): 
                yh = yh[:-1] + "-" + yh[-1]

        # Append suffix to symbol
        yh += MIC_REFERENCE.get(mic, "")

        return yh

        
def get_stock_list() -> List[Dict]:
    """Downloads stock list from Freetrade Google Sheet, and returns as dict"""
    endpoint = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
    return pd.read_csv(endpoint).to_dict(orient='records')


def record_exists(table: object, value: Union[str, int], key: str="isin") -> bool:
    """Checks DynamoDB table for value, returning True/False accordingly"""
    response = table.get_item(key={key: value})

    if "Item" in response:
        return True
    else:
        return False

    # TODO: test using localstack



def lambda_handler(event, context):

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('your_table_name')

    requests_cache.install_cache(
        "stock_requests_cache", 
        expire_after=REQUESTS_CACHE_TTL
    )

    stock_list = get_stock_list()

    random.shuffle(stock_list)

    chosen_records = []

    count = 0
    for record in stock_list:
        
        try:
            model = FreetradeModel(**record)
        except ISINFormatError:
            continue    # TODO: log this
        except pydantic.error_wrappers.ValidationError:
            continue    # TODO: log this
        except ISAEligibilityError:
            continue    # TODO: log this
        
        # check if stock already exists in dynamoDB, 
        # using record exists function
            # if does then skip
            # else continue

        chosen_records.append(record)

        count += 1
        if count > LIMIT:
            break

    return chosen_records



        
        
    


    # try to download key financial data from Yahoo
        # run through pydantic model & log issues
        # Any issues need to be logged
        # Errors here will not be skipped

    # Update DynamoDB table accordingly
    # and repeat until a defined limit (defined in OS environment?)





