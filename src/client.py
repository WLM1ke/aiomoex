"""Асинхронный клиент для MOEX ISS"""
import collections

import aiohttp
from aiohttp import client_exceptions

BASE_QUERY = {'iss.json': 'extended', 'iss.meta': 'off'}


class ISSMoexError(Exception):
    pass


class ISSClient:
    """Асинхронный клиент для MOEX ISS

    Загружает данные для простых ответов с помощью метода get. Для ответов состоящих из некольких блоков данных
    реализован асинхронный генератов отдельных блоков и метод их сбора get_all
    """
    def __init__(self, url: str, query: dict = None):
        """MOEX ISS является REST сервером

        Полный перечень запросов и параметров к ним https://iss.moex.com/iss/reference/
        Дополнительное описание https://fs.moex.com/files/6523

        :param url: адрес запроса
        :param query: перечень дополнительных параметров запроса. К списку дополнительных параметров всегда добавляется
        требование предоставить ответ ввиде расширенного json без метаданных
        """
        self._url = url
        self._query = query or dict()

    def __repr__(self):
        return f'{self.__class__.__name__}(url={self._url}, query={self._query})'

    async def __aiter__(self):
        """Асинхронный генератор по ответам состоящим из нескольких блоков

        На часть запросов выдается только начальный блок данных (обычно из 100 элементов). Генератор обеспечивает
        загрузку всех блоков. При этом в ответах на некоторые запросы может содержаться курсор с положением текущего
        блока данных (позволяет сэкономить один запрос). Генератор обеспечивает обработку ответов как с курсором, так и
        без него
        """
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

    async def get(self, start=None) -> dict:
        """Загрузка данных

        :param start: Номер элемента с которого нужно вывести данные. Используется для дозагрузки данных, состоящих из
        нескольких блоков
        :return: Блок данных из ответа с отброшенной вспомогательной информацией - словарь, каждый ключь котрого
        соответсвует одной из таблиц с данными. Таблицы являются списками словарей, которые напрямую конвертируются в
        pandas.DataFrame
        """
        url = self._url
        query = self._make_query(start)
        async with aiohttp.ClientSession() as session:
                async with session.get(url, params=query) as respond:
                    try:
                        respond.raise_for_status()
                    except client_exceptions.ClientResponseError:
                        raise ISSMoexError('Неверный url', respond.url)
                    else:
                        data = await respond.json()
                        return data[1]

    def _make_query(self, start=None):
        """К общему набору парметров запроса добавляется требование предоставить ответ ввиде расширенного json"""
        params = collections.ChainMap(dict(), BASE_QUERY, self._query)
        if start:
            params['start'] = start
        return params

    async def get_all(self) -> dict:
        """Собирает данные данные для запросов, ответы на которые выдаются отдельными блоками

        :return: Блок данных из ответа с отброшенной вспомогательной информацией - словарь, каждый ключь котрого
        соответсвует одной из таблиц с данными. Таблицы являются списками словарей, которые напрямую конвертируются в
        pandas.DataFrame
        """
        all_data = dict()
        async for data in self:
            for key, value in data.items():
                all_data.setdefault(key, []).extend(value)
        return all_data
