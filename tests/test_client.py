import typing

import pytest

from aiomoex import client


@pytest.mark.asyncio
async def test_start_close_session():
    cls = client.ISSClient
    assert cls.is_session_closed()
    cls.start_session()
    assert not cls.is_session_closed()
    with pytest.raises(client.ISSMoexError) as error:
        cls.start_session()
    assert 'Сессия для работы с MOEX ISS уже создана' == str(error.value)
    await cls.close_session()
    assert cls.is_session_closed()
    with pytest.raises(client.ISSMoexError) as error:
        await cls.close_session()
    assert 'Сессия для работы с MOEX ISS уже закрыта' == str(error.value)


@pytest.fixture
async def manage_session():
    cls = client.ISSClient
    cls.start_session()
    yield
    await cls.close_session()


def test_iss_client_async_iterable():
    iss = client.ISSClient('test_url')
    assert isinstance(iss, typing.AsyncIterable)
    assert str(iss) == 'ISSClient(url=test_url, query={})'


def test_make_query_empty():
    iss = client.ISSClient('test_url')
    # noinspection PyProtectedMember
    query = iss._make_query()
    assert isinstance(query, typing.Mapping)
    assert len(query) == 2
    assert query['iss.json'] == 'extended'
    assert query['iss.meta'] == 'off'


def test_make_query_not_empty():
    iss = client.ISSClient('test_url', dict(test_param='test_value'))
    # noinspection PyProtectedMember
    query = iss._make_query()
    assert isinstance(query, typing.Mapping)
    assert len(query) == 3
    assert query['iss.json'] == 'extended'
    assert query['iss.meta'] == 'off'
    assert query['test_param'] == 'test_value'


def test_make_query_not_empty_with_start():
    iss = client.ISSClient('test_url', dict(test_param='test_value'))
    # noinspection PyProtectedMember
    query = iss._make_query(100)
    assert isinstance(query, typing.Mapping)
    assert len(query) == 4
    assert query['iss.json'] == 'extended'
    assert query['iss.meta'] == 'off'
    assert query['test_param'] == 'test_value'
    assert query['start'] == 100


@pytest.mark.asyncio
@pytest.mark.usefixtures('manage_session')
async def test_get():
    url = 'https://iss.moex.com/iss/securities.json'
    query = dict(q='1-02-65104-D')
    iss = client.ISSClient(url, query)
    raw = await iss.get()
    data = raw['securities']
    assert isinstance(data, list)
    assert len(data) == 4
    assert isinstance(data[0], dict)
    assert data[1]['regnumber'] == '1-02-65104-D'
    assert 'Юнипро' in data[2]['emitent_title']


@pytest.mark.asyncio
@pytest.mark.usefixtures('manage_session')
async def test_get_with_start():
    url = 'https://iss.moex.com/iss/securities.json'
    query = dict(q='1-02-65104-D')
    iss = client.ISSClient(url, query)
    raw = await iss.get(1)
    data = raw['securities']
    assert isinstance(data, list)
    assert len(data) == 3
    assert isinstance(data[0], dict)
    assert data[1]['regnumber'] == '1-02-65104-D'
    assert 'Юнипро' in data[2]['emitent_title']


@pytest.mark.asyncio
@pytest.mark.usefixtures('manage_session')
async def test_get_error():
    url = 'https://iss.moex.com/iss/securities1.json'
    iss = client.ISSClient(url)
    with pytest.raises(client.ISSMoexError) as error:
        await iss.get()
    assert 'Неверный url' in str(error.value)
    assert 'url' in str(error.value)


@pytest.mark.asyncio
@pytest.mark.usefixtures('manage_session')
async def test_get_all_with_cursor():
    url = 'https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/SNGSP.json'
    query = {'from': '2018-01-01', 'till': '2018-03-01'}
    iss = client.ISSClient(url, query)
    raw = await iss.get_all()
    data = raw['history']
    assert isinstance(data, list)
    assert len(data) > 100
    assert data[0]['TRADEDATE'] == '2018-01-03'
    assert data[-1]['TRADEDATE'] == '2018-03-01'
    for row in data:
        for column in ['TRADEDATE', 'OPEN', 'LOW', 'HIGH', 'CLOSE', 'VOLUME']:
            assert column in row


@pytest.mark.asyncio
@pytest.mark.usefixtures('manage_session')
async def test_get_all_without_cursor():
    url = 'https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/SNGSP.json'
    query = {'from': '2018-01-03', 'till': '2018-06-01'}
    iss = client.ISSClient(url, query)
    raw = await iss.get_all()
    data = raw['history']
    assert isinstance(data, list)
    assert len(data) > 100
    assert data[0]['TRADEDATE'] == '2018-01-03'
    assert data[-1]['TRADEDATE'] == '2018-06-01'
    for row in data:
        for column in ['TRADEDATE', 'OPEN', 'LOW', 'HIGH', 'CLOSE', 'VOLUME']:
            assert column in row


@pytest.mark.asyncio
async def test_get_all_error(monkeypatch):
    iss = client.ISSClient('')
    data = {'history.cursor': [0, 1]}

    async def fake_get(_):
        return data

    monkeypatch.setattr(iss, 'get', fake_get)
    with pytest.raises(client.ISSMoexError) as error:
        await iss.get_all()
    assert f'Некорректные данные history.cursor: {data["history.cursor"]}' in str(error.value)
