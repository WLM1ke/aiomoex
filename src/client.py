"""Асинхронный клиент для MOEX ISS"""
import collections

import aiohttp
from aiohttp import client_exceptions

BASE_QUERY = {'iss.json': 'extended', 'iss.meta': 'off'}


class ISSMoexError(Exception):
    pass


class ISSClient:
    """"""
    def __init__(self, url, query: dict = None):
        self._url = url
        self._query = query or dict()

    async def get(self, start=None):
        url = self._url
        query = self._make_query(start)
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                async with session.get(url, params=query) as respond:
                    data = await respond.json()
                    return data[1]
            except client_exceptions.ClientResponseError:
                raise ISSMoexError('Неверный url', url, dict(query))

    def _make_query(self, start=None):
        params = collections.ChainMap(dict(), BASE_QUERY, self._query)
        if start:
            params['start'] = start
        return params

    async def yield_data(self):
        start = 0
        while start is not None:
            data = await self.get(start)
            if 'history.cursor' in data:
                if len(data['history.cursor']) != 1:
                    raise ISSMoexError('Некорректные данные history.cursor: {cursor}')
                cursor = data['history.cursor'][0]
                if cursor['INDEX'] + cursor['PAGESIZE'] < cursor['TOTAL']:
                    start += cursor['PAGESIZE']
                else:
                    start = None
                del data['history.cursor']
                yield data
            else:
                block_size = len(data[next(iter(data))])
                if block_size:
                    start += block_size
                    yield data
                else:
                    start = None

    async def get_all(self):
        all_data = dict()
        async for data in self.yield_data():
            for key in data:  # TODO: Убрать и разобраться с unpack
                all_data.setdefault(key, []).extend(data[key])
        return all_data


