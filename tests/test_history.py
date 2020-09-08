import pytest
import pandas as pd

from aiomoex import history


@pytest.mark.asyncio
async def test_get_board_dates(http_session):
    data = await history.get_board_dates(http_session)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["from"] == "1997-03-24"
    assert data[0]["till"] >= "2018-11-27"


@pytest.mark.asyncio
async def test_get_board_securities(http_session):
    data = await history.get_board_securities(http_session)
    assert isinstance(data, list)
    assert len(data) > 200
    df = pd.DataFrame(data)
    df.set_index("SECID", inplace=True)
    assert df.loc["AKRN", "SHORTNAME"] == "Акрон"
    assert df.loc["GAZP", "REGNUMBER"] == "1-02-00028-A"
    assert df.loc["TTLK", "LOTSIZE"] == 10000
    assert df.loc["MRSB", "SHORTNAME"] == "МордЭнСб"
    assert df.loc["MRSB", "REGNUMBER"] == "1-01-55055-E"
    assert df.loc["MRSB", "LOTSIZE"] == 10000
    assert df.index[0] == "ABRD"
    assert df["SHORTNAME"].iat[0] == "АбрауДюрсо"
    assert df["REGNUMBER"].iat[0] == "1-02-12500-A"
    assert df["LOTSIZE"].iat[0] == 10
    assert df["SHORTNAME"].iat[-1] == "ЗВЕЗДА ао"
    assert df["REGNUMBER"].iat[-1] == "1-01-00169-D"
    assert df["LOTSIZE"].iat[-1] == 1000
    assert df.index[-1] == "ZVEZ"


@pytest.mark.asyncio
async def test_get_market_history_from_beginning(http_session):
    data = await history.get_market_history(http_session, "AKRN", end="2006-12-01")
    assert isinstance(data, list)
    assert data[0]["TRADEDATE"] == "2006-10-11"
    assert data[-1]["TRADEDATE"] == "2006-12-01"
    assert len(data[-2]) == 5
    assert "CLOSE" in data[2]
    assert "VOLUME" in data[3]


@pytest.mark.asyncio
async def test_get_market_history_to_end(http_session):
    data = await history.get_market_history(http_session, "MOEX", start="2017-10-02")
    assert isinstance(data, list)
    assert len(data) > 100
    assert data[0]["TRADEDATE"] == "2017-10-02"
    assert data[-1]["TRADEDATE"] >= "2018-11-19"


@pytest.mark.asyncio
async def test_get_board_history_from_beginning(http_session):
    data = await history.get_board_history(http_session, "LSNGP", end="2014-08-01")
    df = pd.DataFrame(data)
    df.set_index("TRADEDATE", inplace=True)
    assert len(df.columns) == 4
    assert df.index[0] == "2014-06-09"
    assert df.at["2014-06-09", "CLOSE"] == pytest.approx(14.7)
    assert df.at["2014-08-01", "VOLUME"] == 4000


@pytest.mark.asyncio
async def test_get_board_history_to_end(http_session):
    data = await history.get_board_history(http_session, "LSRG", start="2018-08-07")
    df = pd.DataFrame(data)
    df.set_index("TRADEDATE", inplace=True)
    assert len(df.columns) == 4
    assert df.index[0] == "2018-08-07"
    assert df.index[-1] >= "2018-11-19"
    assert df.at["2018-08-07", "CLOSE"] == 777
    assert df.at["2018-08-10", "VOLUME"] == 11313
    assert df.at["2018-08-10", "BOARDID"] == "TQBR"
    assert df.at["2018-08-10", "VALUE"] == pytest.approx(8_626_464.5)
    assert df.at["2018-09-06", "CLOSE"] == pytest.approx(660)
    assert df.at["2018-08-28", "VOLUME"] == 47428
