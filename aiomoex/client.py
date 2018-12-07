"""Асинхронный клиент для MOEX ISS"""
import collections
from collections import abc

import aiohttp
from aiohttp import client_exceptions

BASE_QUERY = {"iss.json": "extended", "iss.meta": "off"}


class ISSMoexError(Exception):
    pass


class ISSClient(abc.AsyncIterable):
    """Асинхронный клиент для MOEX ISS - может быть использован с async for

    Для работы клиентов необходимо начать сессию соединений с MOEX ISS (общая для всех клиентов). А после
    окончания использования всех клиентов закрыть сессию для высвобождения ресурсов

    Загружает данные для простых ответов с помощью метода get. Для ответов состоящих из нескольких блоков данных
    поддерживается протокол асинхронного генератора отдельных блоков или метод get_all для их автоматического сбора
    """

    _client_session = None

    def __init__(self, url: str, query: dict = None):
        """MOEX ISS является REST сервером

        Полный перечень запросов и параметров к ним https://iss.moex.com/iss/reference/
        Дополнительное описание https://fs.moex.com/files/6523

        :param url: адрес запроса
        :param query: перечень дополнительных параметров запроса. К списку дополнительных параметров всегда добавляется
        требование предоставить ответ в виде расширенного json без метаданных
        """
        self._url = url
        self._query = query or dict()

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self._url}, query={self._query})"

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
            if "history.cursor" in data:
                if len(data["history.cursor"]) != 1:
                    raise ISSMoexError(
                        f'Некорректные данные history.cursor: {data["history.cursor"]}'
                    )
                cursor = data["history.cursor"][0]
                if cursor["INDEX"] + cursor["PAGESIZE"] < cursor["TOTAL"]:
                    start += cursor["PAGESIZE"]
                else:
                    start = None
                del data["history.cursor"]
                yield data
            else:
                block_size = len(data[next(iter(data))])
                if block_size:
                    start += block_size
                else:
                    start = None
                yield data

    @classmethod
    def start_session(cls):
        """Создает aiohttp.ClientSession для работы с MOEX ISS"""
        if cls.is_session_closed():
            cls._client_session = aiohttp.ClientSession()
        else:
            raise ISSMoexError("Сессия для работы с MOEX ISS уже создана")

    @classmethod
    async def close_session(cls):
        """Закрывает aiohttp.ClientSession для работы с MOEX ISS"""
        if not cls.is_session_closed():
            await cls._client_session.close()
        else:
            raise ISSMoexError("Сессия для работы с MOEX ISS уже закрыта")

    @classmethod
    def is_session_closed(cls):
        """Закрыта ли сессия соединений с MOEX ISS"""
        if cls._client_session is None or cls._client_session.closed:
            return True
        return False

    async def get(self, start=None):
        """Загрузка данных

        :param start:
            Номер элемента с которого нужно загрузить данные. Используется для дозагрузки данных, состоящих из
            нескольких блоков. При отсутствии данные загружаются с начального элемента

        :return:
            Блок данных с отброшенной вспомогательной информацией - словарь, каждый ключ которого
            соответствует одной из таблиц с данными. Таблицы являются списками словарей, которые напрямую конвертируются
            в pandas.DataFrame
        """
        if not self.is_session_closed():
            session = self._client_session
        else:
            raise ISSMoexError("Откройте сессию для работы с MOEX ISS")
        url = self._url
        query = self._make_query(start)
        async with session.get(url, params=query) as respond:
            try:
                respond.raise_for_status()
            except client_exceptions.ClientResponseError:
                raise ISSMoexError("Неверный url", respond.url)
            else:
                data = await respond.json()
                return data[1]

    def _make_query(self, start=None):
        """К общему набору параметров запроса добавляется требование предоставить ответ в виде расширенного json"""
        params = collections.ChainMap(dict(), BASE_QUERY, self._query)
        if start:
            params["start"] = start
        return params

    async def get_all(self):
        """Собирает все блоки данных для запросов, ответы на которые выдаются по частям отдельными блоками

        :return:
            Объединенные из всех блоков данные с отброшенной вспомогательной информацией - словарь, каждый ключ которого
            соответствует одной из таблиц с данными. Таблицы являются списками словарей, которые напрямую конвертируются
            в pandas.DataFrame
        """
        all_data = dict()
        async for data in self:
            for key, value in data.items():
                all_data.setdefault(key, []).extend(value)
        return all_data
