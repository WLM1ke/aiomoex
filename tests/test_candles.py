import pytest
import pandas as pd

from aiomoex import candles


@pytest.mark.asyncio
async def test_get_market_candle_borders(http_session):
    data = await candles.get_market_candle_borders(http_session, "SNGSP")
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
async def test_get_board_candle_borders(http_session):
    data = await candles.get_board_candle_borders(http_session, "UPRO")
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
async def test_get_market_candles_from_beginning(http_session):
    data = await candles.get_market_candles(http_session, "RTKM", interval=1, end="2011-12-16")
    assert isinstance(data, list)
    assert len(data) > 500
    assert len(data[0]) == 8
    assert data[0]["open"] == pytest.approx(141.55)
    assert data[1]["close"] == pytest.approx(141.59)
    assert data[2]["high"] == pytest.approx(142.4)
    assert data[3]["low"] == pytest.approx(140.81)
    assert data[4]["value"] == pytest.approx(2_586_296.9)
    assert data[5]["volume"] == pytest.approx(4140)
    assert data[6]["begin"] == "2011-12-15 10:06:00"
    assert data[-1]["end"] == "2011-12-16 18:44:59"


@pytest.mark.asyncio
async def test_get_market_candles_to_end(http_session):
    data = await candles.get_market_candles(http_session, "LSRG", interval=24, start="2020-08-20")
    assert isinstance(data, list)
    assert len(data) > 13
    assert len(data[0]) == 8
    assert data[0]["open"] == pytest.approx(775.4)
    assert data[1]["close"] == pytest.approx(771.8)
    assert data[2]["high"] == pytest.approx(779.8)
    assert data[3]["low"] == pytest.approx(770.2)
    assert data[4]["value"] == pytest.approx(59495740.6)
    assert data[6]["begin"] == "2020-08-28 00:00:00"


@pytest.mark.asyncio
async def test_get_market_candles_empty(http_session):
    data = await candles.get_market_candles(http_session, "KSGR", interval=24)
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_board_candles_from_beginning(http_session):
    data = await candles.get_board_candles(http_session, "MTSS", interval=10, end="2011-12-22")
    assert isinstance(data, list)
    assert len(data) > 500
    assert len(data[0]) == 8
    assert data[0]["open"] == pytest.approx(202.7)
    assert data[1]["close"] == pytest.approx(204.12)
    assert data[2]["high"] == pytest.approx(205)
    assert data[3]["low"] == pytest.approx(204.93)
    assert data[4]["value"] == pytest.approx(3_990_683.9)
    assert data[5]["volume"] == pytest.approx(3000)
    assert data[6]["begin"] == "2011-12-08 11:00:00"
    assert data[-1]["end"] == "2011-12-22 18:49:59"


@pytest.mark.asyncio
async def test_get_board_candles_to_end(http_session):
    data = await candles.get_board_candles(http_session, "TTLK", interval=31, start="2014-07-01")
    assert isinstance(data, list)
    assert len(data) > 52
    assert len(data[0]) == 8
    assert data[0]["open"] == pytest.approx(0.152)
    assert data[1]["close"] == pytest.approx(0.15689)
    assert data[2]["high"] == pytest.approx(0.15998)
    assert data[3]["low"] == pytest.approx(0.149)
    assert data[4]["value"] == pytest.approx(2_713_625)
    assert data[5]["volume"] == pytest.approx(20_180_000)
    assert data[6]["begin"] == "2015-01-01 00:00:00"
    assert data[51]["end"] == "2018-10-31 00:00:00"
