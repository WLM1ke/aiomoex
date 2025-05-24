import typing

import pytest

from aiomoex import client


def test_iss_client_async_iterable(http_session) -> None:
    iss = client.ISSClient(http_session, "test_url")
    assert isinstance(iss, typing.AsyncIterable)
    assert str(iss) == "ISSClient(url=test_url, query={})"


def test_make_query_empty(http_session) -> None:
    iss = client.ISSClient(http_session, "test_url")
    # noinspection PyProtectedMember
    query = iss._make_query()
    assert isinstance(query, typing.Mapping)
    assert len(query) == 2
    assert query["iss.json"] == "extended"
    assert query["iss.meta"] == "off"


def test_make_query_not_empty(http_session) -> None:
    iss = client.ISSClient(http_session, "test_url", {"test_param": "test_value"})
    # noinspection PyProtectedMember
    query = iss._make_query()
    assert isinstance(query, typing.Mapping)
    assert len(query) == 3
    assert query["iss.json"] == "extended"
    assert query["iss.meta"] == "off"
    assert query["test_param"] == "test_value"


def test_make_query_not_empty_with_start(http_session) -> None:
    iss = client.ISSClient(http_session, "test_url", {"test_param": "test_value"})
    # noinspection PyProtectedMember
    query = iss._make_query(100)
    assert isinstance(query, typing.Mapping)
    assert len(query) == 4
    assert query["iss.json"] == "extended"
    assert query["iss.meta"] == "off"
    assert query["test_param"] == "test_value"
    assert query["start"] == 100


async def test_get(http_session) -> None:
    url = "https://iss.moex.com/iss/securities.json"
    query = {"q": "1-02-65104-D"}
    iss = client.ISSClient(http_session, url, query)
    raw = await iss.get()
    data = raw["securities"]
    assert isinstance(data, list)
    assert len(data) == 4
    assert isinstance(data[0], dict)
    assert data[1]["regnumber"] == "1-02-65104-D"
    assert "Юнипро" in data[2]["emitent_title"]


async def test_get_with_start(http_session) -> None:
    url = "https://iss.moex.com/iss/securities.json"
    query = {"q": "1-02-65104-D"}
    iss = client.ISSClient(http_session, url, query)
    raw = await iss.get(1)
    data = raw["securities"]
    assert isinstance(data, list)
    assert len(data) == 3
    assert isinstance(data[0], dict)
    assert data[1]["regnumber"] == "1-02-65104-D"
    assert "Юнипро" in data[2]["emitent_title"]


async def test_get_error(http_session) -> None:
    url = "https://iss.moex.com/iss/securities1.json"
    iss = client.ISSClient(http_session, url)
    with pytest.raises(client.ISSMoexError) as error:
        await iss.get()
    assert "Неверный url" in str(error.value)
    assert "url" in str(error.value)


async def test_get_all_with_cursor(http_session) -> None:
    url = "https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/SNGSP.json"
    query = {"from": "2018-01-01", "till": "2018-03-01"}
    iss = client.ISSClient(http_session, url, query)
    raw = await iss.get_all()
    data = raw["history"]
    assert isinstance(data, list)
    assert len(data) > 100
    assert data[0]["TRADEDATE"] == "2018-01-03"
    assert data[-1]["TRADEDATE"] == "2018-03-01"
    for row in data:
        for column in ["TRADEDATE", "OPEN", "LOW", "HIGH", "CLOSE", "VOLUME"]:
            assert column in row


async def test_get_all_without_cursor(http_session) -> None:
    url = "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/SNGSP.json"
    query = {"from": "2018-01-03", "till": "2018-06-01"}
    iss = client.ISSClient(http_session, url, query)
    raw = await iss.get_all()
    data = raw["history"]
    assert isinstance(data, list)
    assert len(data) > 100
    assert data[0]["TRADEDATE"] == "2018-01-03"
    assert data[-1]["TRADEDATE"] == "2018-06-01"
    for row in data:
        for column in ["TRADEDATE", "OPEN", "LOW", "HIGH", "CLOSE", "VOLUME"]:
            assert column in row


def test_cursor_block_size() -> None:
    assert client._cursor_block_size(5, [{"INDEX": 5, "PAGESIZE": 8, "TOTAL": 14}]) == 8


def test_cursor_block_size_zero() -> None:
    assert client._cursor_block_size(5, [{"INDEX": 5, "PAGESIZE": 8, "TOTAL": 13}]) == 0


def test_cursor_block_size_raise_bad_start() -> None:
    with pytest.raises(client.ISSMoexError) as error:
        client._cursor_block_size(5, [{"INDEX": 6, "PAGESIZE": 8, "TOTAL": 14}])
    assert "Некорректные данные history.cursor" in str(error.value)


def test_cursor_block_size_raise_bad_structure() -> None:
    with pytest.raises(client.ISSMoexError) as error:
        client._cursor_block_size(5, [{}, {}])
    assert "Некорректные данные history.cursor" in str(error.value)
