import os
import random
from typing import Dict, List, Optional, Union

import boto3
import pandas as pd
import pydantic
from aws_lambda_powertools import Logger
from pydantic import BaseModel, Field

logger = Logger()

SHEET_ID = "14Ep-CmoqWxrMU8HshxthRcdRW8IsXvh3n2-ZHVCzqzQ"
GID = "1855920257"
ISA_ELIGIBLE = True
REMOVE_ETF = True
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


class ETFFilterError(Exception):
    """Custom error which is raised when stock is an ETF/ETC"""

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


    @pydantic.validator("long_title", "subtitle")
    @classmethod
    def ETF_filter(cls, value):
        """Filter out ETFs and ETCs from stock list"""

        if not REMOVE_ETF:
            pass

        elif "ETF" in value:
            raise ETFFilterError(value=value, message="ETF stock excluded.")

        elif "ETC" in value:
            raise ETFFilterError(value=value, message="ETC stock excluded.")

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

    endpoint = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

    return pd.read_csv(endpoint).to_dict(orient='records')


def shuffle_and_filter_stock_list(records: List[Dict], sample: int=5) -> List[Dict]:
    """Return a random sample of eligible stocks"""
    
    random.shuffle(records)

    filtered_records = []

    for record in records:
        
        try:
            model = FreetradeModel(**record)

        except ISINFormatError as e:
            logger.warning(f"{record['Title']} excluded. Reason: {e}")
            continue

        except pydantic.error_wrappers.ValidationError as e:
            logger.warning(f"{record} excluded. Reason: Generic validation error")
            continue

        except ISAEligibilityError as e:
            logger.info(f"{record['Title']} excluded. Reason: {e}")
            continue

        except ETFFilterError as e:
            logger.info(f"{record['Title']} excluded. Reason: {e}")
            continue
        
        filtered_records.append(record)

        if len(filtered_records) == sample:
            break
    
    return filtered_records


def lambda_handler(event, context):
    """Lambda function which downloads and checks stocks from Freetrade stock list,
    returning list of eligible stocks. 

    Loops through records in shuffled table, filtering stocks based on:
    - ISA eligibility
    - companies only (excluding ETFs and ETCs)
    - validated ISIN
    - expected data types

    Additionally, creates new data:
    - Yahoo symbol, based on symbol & MIC

    List is returned containing eligible records. 

    Parameters
    ----------
    event: dict, required
        Input event to the Lambda function

    context: object, required
        Lambda Context runtime methods and attributes

    Returns
    ------
        list[dict]: List of eligible stocks including basic information
    """

    records = get_stock_list()

    filtered_records = shuffle_and_filter_stock_list(records, sample=5)

    return filtered_records