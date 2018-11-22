import typing

import pandas as pd
import pytest

import aiomoex
from aiomoex import requests
from aiomoex import client


@pytest.mark.asyncio
async def test_iss_client_session():
    assert issubclass(requests.ISSClientSession, typing.AsyncContextManager)
    async with requests.ISSClientSession() as session:
        assert not session.closed
    assert session.closed


@pytest.fixture
async def iss_client_session():
    async with requests.ISSClientSession():
        yield


def test_make_query_empty():
    # noinspection PyProtectedMember
    query = requests._make_query()
    assert query == {}


def test_make_query_full():
    # noinspection PyProtectedMember
    query = requests._make_query(start=1, end=2, table=3, columns=('4',))
    assert isinstance(query, dict)
    assert len(query) == 4
    assert query['from'] == 1
    assert query['till'] == 2
    assert query['iss.only'] == f'3,history.cursor'
    assert query[f'{3}.columns'] == '4'


def test_make_query_many_columns():
    # noinspection PyProtectedMember
    query = requests._make_query(table=1, columns=('2', '3'))
    assert isinstance(query, dict)
    assert len(query) == 2
    assert query['iss.only'] == f'1,history.cursor'
    assert query[f'{1}.columns'] == '2,3'


check_points = [('1-02-65104-D', {'UPRO', 'EONR', 'OGK4'}),
                ('10301481B', {'SBER', 'SBER03'}),
                ('20301481B', {'SBERP', 'SBERP03'}),
                ('1-02-06556-A', {'PHOR'})]


@pytest.mark.parametrize("reg_number, expected", check_points)
@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_find_find_securities(reg_number, expected):
    data = await aiomoex.find_securities(reg_number)
    assert isinstance(data, list)
    assert expected == {row['secid'] for row in data if row['regnumber'] == reg_number}


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_board_securities():
    data = await aiomoex.get_board_securities()
    assert isinstance(data, list)
    assert len(data) > 200
    df = pd.DataFrame(data)
    df.set_index('SECID', inplace=True)
    assert df.loc['AKRN', 'SHORTNAME'] == 'Акрон'
    assert df.loc['GAZP', 'REGNUMBER'] == '1-02-00028-A'
    assert df.loc['TTLK', 'LOTSIZE'] == 10000
    assert df.loc['MRSB', 'SHORTNAME'] == 'МордЭнСб'
    assert df.loc['MRSB', 'REGNUMBER'] == '1-01-55055-E'
    assert df.loc['MRSB', 'LOTSIZE'] == 10000
    assert df.index[0] == 'ABRD'
    assert df['SHORTNAME'].iat[0] == 'АбрауДюрсо'
    assert df['REGNUMBER'].iat[0] == '1-02-12500-A'
    assert df['LOTSIZE'].iat[0] == 10
    assert df['SHORTNAME'].iat[-1] == 'ЗВЕЗДА ао'
    assert df['REGNUMBER'].iat[-1] == '1-01-00169-D'
    assert df['LOTSIZE'].iat[-1] == 1000
    assert df.index[-1] == 'ZVEZ'


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_market_history_from_beginning():
    data = await aiomoex.get_market_history('AKRN', end='2006-12-01')
    assert isinstance(data, list)
    assert data[0]['TRADEDATE'] == '2006-10-11'
    assert data[-1]['TRADEDATE'] == '2006-12-01'
    assert len(data[-2]) == 3
    assert 'CLOSE' in data[2]
    assert 'VOLUME' in data[3]


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_market_history_to_end():
    data = await aiomoex.get_market_history('MOEX', start='2017-10-02')
    assert isinstance(data, list)
    assert len(data) > 100
    assert data[0]['TRADEDATE'] == '2017-10-02'
    assert data[-1]['TRADEDATE'] >= '2018-11-19'


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_history_error():
    with pytest.raises(client.ISSMoexError) as error:
        await aiomoex.get_board_history('XXXX')
    assert 'Отсутсвуют исторические котировки для' in str(error)


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_board_history_from_beginning():
    data = await aiomoex.get_board_history('LSNGP', end='2014-08-01')
    df = pd.DataFrame(data)
    df.set_index('TRADEDATE', inplace=True)
    assert len(df.columns) == 2
    assert df.index[0] == '2014-06-09'
    assert df.at['2014-06-09', 'CLOSE'] == pytest.approx(14.7)
    assert df.at['2014-08-01', 'VOLUME'] == 4000


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_board_history_to_end():
    data = await aiomoex.get_board_history('LSRG', start='2018-08-07')
    df = pd.DataFrame(data)
    df.set_index('TRADEDATE', inplace=True)
    assert len(df.columns) == 2
    assert df.index[0] == '2018-08-07'
    assert df.index[-1] >= '2018-11-19'
    assert df.at['2018-08-07', 'CLOSE'] == 777
    assert df.at['2018-08-10', 'VOLUME'] == 11313
    assert df.at['2018-09-06', 'CLOSE'] == pytest.approx(660)
    assert df.at['2018-08-28', 'VOLUME'] == 47428


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_index_history_from_beginning():
    data = await aiomoex.get_index_history(end='2003-08-01')
    df = pd.DataFrame(data)
    df.set_index('TRADEDATE', inplace=True)
    assert len(df.columns) == 1
    assert df.size > 100
    assert df.index[0] == '2003-02-26'
    assert df.at['2003-02-26', 'CLOSE'] == pytest.approx(335.67)


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_index_history_to_end():
    data = await aiomoex.get_index_history(start='2017-10-02')
    df = pd.DataFrame(data)
    df.set_index('TRADEDATE', inplace=True)
    assert len(df.columns) == 1
    assert df.size > 100
    assert df.index[0] == '2017-10-02'
    assert df.index[-1] >= '2018-11-19'
    assert df.at['2018-03-02', 'CLOSE'] == pytest.approx(3273.16)
