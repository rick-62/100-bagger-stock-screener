import os
import random

import pandas as pd
import pydantic

from pydantic import BaseModel, Field
from typing import List, Dict


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


    @pydantic.validator("yahoo_symbol", pre=True)
    @classmethod
    def create_yahoo_symbol(cls, values):
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

        













    # Convert symbols to yahoo symbol, using MIC codes
    # remvove lowercas suffix from symbol
    






def get_stock_list() -> List[Dict]:
    """Downloads stock list from Freetrade Google Sheet, and returns as dictionary"""

    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

    return pd.read_csv(url).to_dict(orient='records')


def lambda_handler(event, context):

    requests_cache.install_cache(
        "stock_requests_cache", 
        expire_after=REQUESTS_CACHE_TTL
    )

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
        except (ISINFormatError, pydantic.error_wrappers.ValidationError):
            pass


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


    
if __name__=="__main__":
    pass




