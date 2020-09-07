import typing

import pandas as pd
import pytest

import aiomoex
import aiomoex.reference
import aiomoex.request_helpers
from aiomoex import history


@pytest.mark.asyncio
async def test_iss_client_session():
    assert issubclass(history.ISSClientSession, typing.AsyncContextManager)
    async with history.ISSClientSession() as session:
        assert not session.closed
    assert session.closed


@pytest.fixture
async def iss_client_session():
    async with history.ISSClientSession():
        yield


def test_make_query_empty():
    # noinspection PyProtectedMember
    query = aiomoex.request_helpers.make_query()
    assert query == {}


def test_make_query_full():
    # noinspection PyProtectedMember
    query = aiomoex.request_helpers.make_query(start=1, end=2, table=3, columns=("4",))
    assert isinstance(query, dict)
    assert len(query) == 4
    assert query["from"] == 1
    assert query["till"] == 2
    assert query["iss.only"] == f"3,history.cursor"
    assert query[f"{3}.columns"] == "4"


def test_make_query_many_columns():
    # noinspection PyProtectedMember
    query = aiomoex.request_helpers.make_query(table=1, columns=("2", "3"))
    assert isinstance(query, dict)
    assert len(query) == 2
    assert query["iss.only"] == f"1,history.cursor"
    assert query[f"{1}.columns"] == "2,3"


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_reference():
    data = await aiomoex.reference.get_reference("engines")
    assert isinstance(data, list)
    assert len(data) == 7
    assert data == [
        {"id": 1, "name": "stock", "title": "Фондовый рынок и рынок депозитов"},
        {"id": 2, "name": "state", "title": "Рынок ГЦБ (размещение)"},
        {"id": 3, "name": "currency", "title": "Валютный рынок"},
        {"id": 4, "name": "futures", "title": "Срочный рынок"},
        {"id": 5, "name": "commodity", "title": "Товарный рынок"},
        {"id": 6, "name": "interventions", "title": "Товарные интервенции"},
        {"id": 7, "name": "offboard", "title": "ОТС-система"},
    ]


check_points = [
    ("1-02-65104-D", {"UPRO", "EONR", "OGK4"}),
    ("10301481B", {"SBER", "SBER03"}),
    ("20301481B", {"SBERP", "SBERP03"}),
    ("1-02-06556-A", {"PHOR"}),
]


@pytest.mark.parametrize("reg_number, expected", check_points)
@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_find_find_securities(reg_number, expected):
    data = await aiomoex.reference.find_securities(reg_number)
    assert isinstance(data, list)
    assert expected == {row["secid"] for row in data if row["regnumber"] == reg_number}


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_market_candle_borders():
    data = await aiomoex.get_market_candle_borders("SNGSP")
    assert isinstance(data, list)
    assert len(data) == 7
    for i in data:
        del i["end"]
    assert data == [
        {"begin": "2011-12-15 10:00:00", "interval": 1, "board_group_id": 57},
        {"begin": "2003-07-01 00:00:00", "interval": 4, "board_group_id": 57},
        {"begin": "2003-07-28 00:00:00", "interval": 7, "board_group_id": 57},
        {"begin": "2011-12-08 10:00:00", "interval": 10, "board_group_id": 57},
        {"begin": "2003-07-31 00:00:00", "interval": 24, "board_group_id": 57},
        {"begin": "2003-07-01 00:00:00", "interval": 31, "board_group_id": 57},
        {"begin": "2011-11-17 10:00:00", "interval": 60, "board_group_id": 57},
    ]


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_board_candle_borders():
    data = await aiomoex.get_board_candle_borders("UPRO")
    assert isinstance(data, list)
    assert len(data) == 7
    for i in data:
        del i["end"]
    assert data == [
        {"begin": "2016-07-01 09:59:00", "interval": 1},
        {"begin": "2016-07-01 00:00:00", "interval": 4},
        {"begin": "2016-06-27 00:00:00", "interval": 7},
        {"begin": "2016-07-01 09:50:00", "interval": 10},
        {"begin": "2016-07-01 00:00:00", "interval": 24},
        {"begin": "2016-07-01 00:00:00", "interval": 31},
        {"begin": "2016-07-01 09:00:00", "interval": 60},
    ]


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_market_candles_from_beginning():
    data = await aiomoex.get_market_candles("RTKM", interval=1, end="2011-12-16")
    assert isinstance(data, list)
    assert len(data) > 500
    df = pd.DataFrame(data)
    assert df.columns.size == 8
    assert df.loc[0, "open"] == pytest.approx(141.55)
    assert df.loc[1, "close"] == pytest.approx(141.59)
    assert df.loc[2, "high"] == pytest.approx(142.4)
    assert df.loc[3, "low"] == pytest.approx(140.81)
    assert df.loc[4, "value"] == pytest.approx(2_586_296.9)
    assert df.loc[5, "volume"] == pytest.approx(4140)
    assert df.loc[6, "begin"] == "2011-12-15 10:06:00"
    assert df.iloc[-1]["end"] == "2011-12-16 18:44:59"


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_market_candles_to_end():
    data = await aiomoex.get_market_candles("LSRG", interval=4, start="2008-01-01")
    assert isinstance(data, list)
    assert len(data) > 47
    df = pd.DataFrame(data)
    assert df.columns.size == 8
    assert df.loc[0, "open"] == pytest.approx(1658)
    assert df.loc[1, "close"] == pytest.approx(1774)
    assert df.loc[2, "high"] == pytest.approx(2400)
    assert df.loc[3, "low"] == pytest.approx(842.0)
    assert df.loc[4, "value"] == pytest.approx(163_600)
    assert df.loc[5, "volume"] == pytest.approx(49400)
    assert df.loc[6, "begin"] == "2009-01-01 00:00:00"
    assert df.loc[46, "end"] == "2018-09-28 00:00:00"


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_market_candles_empty():
    data = await aiomoex.get_market_candles("OGK4", interval=24)
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_board_candles_from_beginning():
    data = await aiomoex.get_board_candles("MTSS", interval=10, end="2011-12-22")
    assert isinstance(data, list)
    assert len(data) > 500
    df = pd.DataFrame(data)
    assert df.columns.size == 8
    assert df.loc[0, "open"] == pytest.approx(202.7)
    assert df.loc[1, "close"] == pytest.approx(204.12)
    assert df.loc[2, "high"] == pytest.approx(205)
    assert df.loc[3, "low"] == pytest.approx(204.93)
    assert df.loc[4, "value"] == pytest.approx(3_990_683.9)
    assert df.loc[5, "volume"] == pytest.approx(3000)
    assert df.loc[6, "begin"] == "2011-12-08 11:00:00"
    assert df.iloc[-1]["end"] == "2011-12-22 18:49:59"


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_board_candles_to_end():
    data = await aiomoex.get_board_candles("TTLK", interval=31, start="2014-07-01")
    assert isinstance(data, list)
    assert len(data) > 52
    df = pd.DataFrame(data)
    assert df.columns.size == 8
    assert df.loc[0, "open"] == pytest.approx(0.152)
    assert df.loc[1, "close"] == pytest.approx(0.15689)
    assert df.loc[2, "high"] == pytest.approx(0.15998)
    assert df.loc[3, "low"] == pytest.approx(0.149)
    assert df.loc[4, "value"] == pytest.approx(2_713_625)
    assert df.loc[5, "volume"] == pytest.approx(20_180_000)
    assert df.loc[6, "begin"] == "2015-01-01 00:00:00"
    assert df.loc[51, "end"] == "2018-10-31 00:00:00"


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_board_dates():
    data = await aiomoex.get_board_dates()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["from"] == "2013-03-25"
    assert data[0]["till"] >= "2018-11-27"


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_board_securities():
    data = await aiomoex.get_board_securities()
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
@pytest.mark.usefixtures("iss_client_session")
async def test_get_market_history_from_beginning():
    data = await aiomoex.get_market_history("AKRN", end="2006-12-01")
    assert isinstance(data, list)
    assert data[0]["TRADEDATE"] == "2006-10-11"
    assert data[-1]["TRADEDATE"] == "2006-12-01"
    assert len(data[-2]) == 5
    assert "CLOSE" in data[2]
    assert "VOLUME" in data[3]


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_market_history_to_end():
    data = await aiomoex.get_market_history("MOEX", start="2017-10-02")
    assert isinstance(data, list)
    assert len(data) > 100
    assert data[0]["TRADEDATE"] == "2017-10-02"
    assert data[-1]["TRADEDATE"] >= "2018-11-19"


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_board_history_from_beginning():
    data = await aiomoex.get_board_history("LSNGP", end="2014-08-01")
    df = pd.DataFrame(data)
    df.set_index("TRADEDATE", inplace=True)
    assert len(df.columns) == 4
    assert df.index[0] == "2014-06-09"
    assert df.at["2014-06-09", "CLOSE"] == pytest.approx(14.7)
    assert df.at["2014-08-01", "VOLUME"] == 4000


@pytest.mark.asyncio
@pytest.mark.usefixtures("iss_client_session")
async def test_get_board_history_to_end():
    data = await aiomoex.get_board_history("LSRG", start="2018-08-07")
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
