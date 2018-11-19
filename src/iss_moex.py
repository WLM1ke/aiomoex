"""Запросы к MOEX ISS и асинхронный клиент"""
from enum import Enum
import collections

import aiohttp

BASE_QUERY = {'iss.json': 'extended', 'iss.meta': 'off'}
FIRST_RESPOND_ELEMENT = {'charsetinfo': {'name': 'utf-8'}}


class BaseMoex(Exception):
    pass


class RequestError(BaseMoex):
    pass


class RespondError(BaseMoex):
    pass


class ISSRequests(Enum):
    """Запросы к MOEX ISS

    Реализована часть запросов, при необходимости могут быть дополненны:
        Полный перечень запросов https://iss.moex.com/iss/reference/
        Дополнительное описание https://fs.moex.com/files/6523
    """
    # https://iss.moex.com/iss/reference/5
    FIND_SECURITIES = 'https://iss.moex.com/iss/securities.json'
    # https://iss.moex.com/iss/reference/32
    GET_BOARD_SECURITIES = 'https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities.json'
    # https://iss.moex.com/iss/reference/63
    GET_MARKET_SECURITY_HISTORY = ('https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/'
                                   'securities/{security}.json')
    # https://iss.moex.com/iss/reference/65
    GET_BOARD_SECURITY_HISTORY = ('https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/'
                                  'boards/{board}/securities/{security}.json')


class ISSClient:
    """"""
    def __init__(self, request: ISSRequests, *, request_params: dict = None, query: dict = None):
        self._request = request
        self._request_params = request_params or dict()
        self._query = query or dict()
        self._start = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._start is None:
            raise StopAsyncIteration
        data = await self.get_data(self._start)
        if 'history.cursor' in data:
            cursor = data['history.cursor']
            if len(cursor) != 1:
                raise RespondError('Wrong history.cursor data: {cursor}')
            if cursor[0]['INDEX'] + cursor[0]['PAGESIZE'] < cursor[0]['TOTAL']:
                self._start += cursor[0]['PAGESIZE']
            else:
                self._start = None
            del data['history.cursor']
            return data
        data_size = len(data[next(iter(data))])
        if data_size:
            self._start += data_size
            return data
        raise StopAsyncIteration

    async def get_data(self, start=None):
        url = self._make_url()
        params = self._make_query(start)
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(url, params=params) as respond:
                data = await respond.json()
                return data[1]

    def _make_url(self):
        try:
            url = self._request.value.format(**self._request_params)
        except KeyError as error:
            raise RequestError(f'Requests {self._request.value} needs "{error.args[0]}" parameter')
        return url

    def _make_query(self, start=None):
        params = collections.ChainMap(dict(), BASE_QUERY, self._query)
        if start:
            params['start'] = start
        return params

    async def get_all_data(self):
        self._start = 0
        all_data = {}
        async for data in self:
            print(self._start)  # TODO: Убрать и разобраться с unpack
            for key in data:
                all_data.setdefault(key, []).extend(data[key])
        return all_data


if __name__ == '__main__':
    import asyncio

    async def run():
        client = ISSClient(ISSRequests.FIND_SECURITIES, query=dict(q='AKRN'))
        # print(await client.get_data())

        request_params = dict(engine='stock', market='shares', board='TQBR')
        client = ISSClient(ISSRequests.GET_BOARD_SECURITIES, request_params=request_params)
        # print(await client.get_data())

        request_params = dict(engine='stock', market='index', board='RTSI', security='MCFTRR')
        query = {'from': '2018-01-01'}
        client = ISSClient(ISSRequests.GET_BOARD_SECURITY_HISTORY, request_params=request_params, query=query)
        print(await client.get_data())
        print(await client.get_all_data())

        request_params = dict(engine='stock', market='shares', security='GAZP')
        query = {'from': '2018-06-01'}
        client = ISSClient(ISSRequests.GET_MARKET_SECURITY_HISTORY, request_params=request_params, query=query)
        print(await client.get_data())
        print(await client.get_all_data())

    loop = asyncio.run(run())
