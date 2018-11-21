import typing

import pytest

from src import client


def test_iss_client_async_iterable():
    iss = client.ISSClient('test_url')
    assert isinstance(iss, typing.AsyncIterable)


def test_make_query_empty():
    iss = client.ISSClient('test_url')
    query = iss._make_query()
    assert isinstance(query, typing.Mapping)
    assert len(query) == 2
    assert query['iss.json'] == 'extended'
    assert query['iss.meta'] == 'off'


def test_make_query_not_empty():
    iss = client.ISSClient('test_url', dict(test_param='test_value'))
    query = iss._make_query()
    assert isinstance(query, typing.Mapping)
    assert len(query) == 3
    assert query['iss.json'] == 'extended'
    assert query['iss.meta'] == 'off'
    assert query['test_param'] == 'test_value'


def test_make_query_not_empty_with_start():
    iss = client.ISSClient('test_url', dict(test_param='test_value'))
    query = iss._make_query(100)
    assert isinstance(query, typing.Mapping)
    assert len(query) == 4
    assert query['iss.json'] == 'extended'
    assert query['iss.meta'] == 'off'
    assert query['test_param'] == 'test_value'
    assert query['start'] == 100


@pytest.mark.asyncio
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
