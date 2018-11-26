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


@pytest.mark.asyncio
@pytest.mark.usefixtures('iss_client_session')
async def test_get_reference():
    data = await aiomoex.get_reference('engines')
    assert isinstance(data, list)
    assert len(data) == 7
    assert data == [{'id': 1, 'name': 'stock', 'title': 'Фондовый рынок и рынок депозитов'},
                    {'id': 2, 'name': 'state', 'title': 'Рынок ГЦБ (размещение)'},
                    {'id': 3, 'name': 'currency', 'title': 'Валютный рынок'},
                    {'id': 4, 'name': 'futures', 'title': 'Срочный рынок'},
                    {'id': 5, 'name': 'commodity', 'title': 'Товарный рынок'},
                    {'id': 6, 'name': 'interventions', 'title': 'Товарные интервенции'},
                    {'id': 7, 'name': 'offboard', 'title': 'ОТС-система'}]


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
async def test_get_candle_borders():
    data = await aiomoex.get_candle_borders('SNGSP')
    assert isinstance(data, list)
    assert len(data) == 7
    assert data == [
        {'begin': '2011-12-15 10:00:00', 'end': '2018-11-23 18:49:59', 'interval': 1, 'board_group_id': 57},
        {'begin': '2003-07-01 00:00:00', 'end': '2018-11-23 00:00:00', 'interval': 4, 'board_group_id': 57},
        {'begin': '2003-07-28 00:00:00', 'end': '2018-11-23 00:00:00', 'interval': 7, 'board_group_id': 57},
        {'begin': '2011-12-08 10:00:00', 'end': '2018-11-23 18:49:59', 'interval': 10, 'board_group_id': 57},
        {'begin': '2003-07-31 00:00:00', 'end': '2018-11-23 23:59:59', 'interval': 24, 'board_group_id': 57},
        {'begin': '2003-07-01 00:00:00', 'end': '2018-11-23 00:00:00', 'interval': 31, 'board_group_id': 57},
        {'begin': '2011-11-17 10:00:00', 'end': '2018-11-23 18:59:59', 'interval': 60, 'board_group_id': 57}]


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
    assert 'Отсутствуют исторические котировки для' in str(error)


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
