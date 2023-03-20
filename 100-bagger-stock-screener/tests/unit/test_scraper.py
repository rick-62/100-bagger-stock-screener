import pytest

from functions.stock_scraper import app

# test pydantic model to esnrue working as intended
# test get stock list

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
    "9gjh4395gj"
])
def test_isin_invalid(value):
    with pytest.raises(app.ISINFormatError):
        app.FreetradeModel.isin_valid(value)
    


# test FreeTradeModel
# try to break it
# what is error message when failure - include in main code, as exception
# try to trigger isin validty checks


def test_get_stock_list():
    pass