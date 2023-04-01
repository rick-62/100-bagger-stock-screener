import pytest
import pandas as pd

from pytest import MonkeyPatch
from unittest.mock import patch, MagicMock, Mock

from functions.stock_scraper import app

@pytest.mark.parametrize("value", [
    "US7835132033", 
    "NL0011585146", 
    "IE00BLLZQ912", 
    "IE00BCRY6557"
])
def test_isin_valid(value):
    assert app.FreetradeModel.isin_valid(value) == value


@pytest.mark.parametrize("value", [
    "EXAI", 
    "US7835132", 
    "7835132033", 
    "US7835132034",
    "",
    "9gjh4395gj",
    "SomethingHere"
])
def test_isin_invalid(value):
    with pytest.raises(app.ISINFormatError):
        app.FreetradeModel.isin_valid(value)


@pytest.mark.parametrize("mic, symbol, yahoo_symbol", [
    ("XNAS", "APPL", "APPL"),
    ("XLON", "FOUR", "FOUR.L"),
    ("XSTO", "LUMI", "LUMI.ST"),
    ("XSTO", "LUMB", "LUM-B.ST"),
    ("XNAS", "PSEC", "PSEC"),
    ("XETR", "TTR1d", "TTR1.DE"),
    ("XWBO", "ANDRv", "ANDR.VI")
])
def test_yahoo_symbol(mic, symbol, yahoo_symbol):
    result = app.FreetradeModel.create_yahoo_symbol(
        None,
        {"mic": mic, "symbol": symbol}
    )
    assert result == yahoo_symbol


def test_isa_eligibility(monkeypatch):

    monkeypatch.setattr('functions.stock_scraper.app.ISA_ELIGIBLE', True)
    app.FreetradeModel.isa_eligibility(True)
    with pytest.raises(app.ISAEligibilityError):
        app.FreetradeModel.isa_eligibility(False)

    monkeypatch.setattr('functions.stock_scraper.app.ISA_ELIGIBLE', False)
    app.FreetradeModel.isa_eligibility(False)
    app.FreetradeModel.isa_eligibility(True)


@pytest.fixture
def FreetradeModel_valid_input():
    return {
        "Title": "test_title",
        "Long_Title": "test_long_title",
        "Subtitle": "test_subtitle",
        "Currency": "GBP",
        "ISA_eligible": True,
        "ISIN": "IE00BCRY6557",
        "MIC": "XLON",
        "Symbol": "EXAI",
        "Fractional_Enabled": True,
    }


def test_FreetradeModel_valid(FreetradeModel_valid_input):
    model = app.FreetradeModel(**FreetradeModel_valid_input)
    assert model.yahoo_symbol == "EXAI.L"


@pytest.mark.parametrize("key, value, exception", [
    ("Title", None, app.pydantic.error_wrappers.ValidationError),
    ("ISA_eligible", "not truthy", app.pydantic.error_wrappers.ValidationError),
    ("ISIN", "US7835132034", app.ISINFormatError)
])
def test_FreetradeModel_invalid(FreetradeModel_valid_input, key, value, exception):
    FreetradeModel_valid_input[key] = value

    with pytest.raises(exception):
        app.FreetradeModel(**FreetradeModel_valid_input)


@patch("functions.stock_scraper.app.pd.read_csv")
def test_get_stock_list(read_csv_mock: Mock):

    read_csv_mock.return_value = pd.DataFrame(
        {"foo": [1, 2, 3], "bar": ["a", "b", "c"]}
    )

    assert app.get_stock_list() == [
        {'foo': 1, 'bar': 'a'},
        {'foo': 2, 'bar': 'b'},
        {'foo': 3, 'bar': 'c'},
    ]
