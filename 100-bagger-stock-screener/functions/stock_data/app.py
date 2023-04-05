
## IN PROGRESS ##


import os
import random

import boto3
import pandas as pd
import pydantic

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union



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





