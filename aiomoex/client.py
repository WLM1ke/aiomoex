"""Асинхронный клиент для MOEX ISS."""
import collections
import types
from typing import AsyncIterable, AsyncIterator, Dict, List, MutableMapping, Optional, Union, cast

import aiohttp
from aiohttp import client_exceptions

Values = Union[str, int, float]
TableRow = Dict[str, Values]
Table = List[TableRow]
TablesDict = Dict[str, Table]
WebQuery = MutableMapping[str, Union[str, int]]

BASE_QUERY = types.MappingProxyType({"iss.json": "extended", "iss.meta": "off"})


class ISSMoexError(Exception):
    """Ошибки во время обработки запросов."""


def _cursor_has_more_data(start: int, cursor_table: Table) -> bool:
    cursor, *wrong_data = cursor_table

    if wrong_data or cast(int, cursor["INDEX"]) != start:
        raise ISSMoexError(f"Некорректные данные history.cursor: {cursor_table}")

    start += cast(int, cursor["PAGESIZE"])
    return start < cast(int, cursor["TOTAL"])


class ISSClient(AsyncIterable[TablesDict]):
    """Асинхронный клиент для MOEX ISS - может быть использован с async for.

    Загружает данные для простых ответов с помощью метода get. Для ответов состоящих из нескольких блоков
    поддер живается протокол асинхронного генератора отдельных блоков или метод get_all для их
    автоматического сбора.
    """

    _client_session = None

    def __init__(self, session: aiohttp.ClientSession, url: str, query: Optional[WebQuery] = None):
        """MOEX ISS является REST сервером.

        Полный перечень запросов и параметров к ним https://iss.moex.com/iss/reference/
        Дополнительное описание https://fs.moex.com/files/6523

        :param session:
            Сессия http соединения.
        :param url:
            Адрес запроса.
        :param query:
            Перечень дополнительных параметров запроса. К списку дополнительных параметров всегда
            добавляется требование предоставить ответ в виде расширенного json без метаданных.
        """
        self._session = session
        self._url = url
        self._query = query or {}

    def __repr__(self) -> str:
        """Наименование класса и содержание запроса к ISS Moex."""
        class_name = self.__class__.__name__
        return f"{class_name}(url={self._url}, query={self._query})"

    def __aiter__(self) -> AsyncIterator[TablesDict]:
        """Асинхронный генератор по ответам состоящим из нескольких блоков.

        На часть запросов выдается только начальный блок данных (обычно из 100 элементов). Генератор
        обеспечивает загрузку всех блоков. При этом в ответах на некоторые запросы может содержаться
        курсор с положением текущего блока данных (позволяет сэкономить один запрос). Генератор
        обеспечивает обработку ответов как с курсором, так и без него.
        """
        return self._iterator_maker()

    async def get(self, start: Optional[int] = None) -> TablesDict:
        """Загрузка данных.

        :param start:
            Номер элемента с которого нужно загрузить данные. Используется для дозагрузки данных,
            состоящих из нескольких блоков. При отсутствии данные загружаются с начального элемента.

        :return:
            Блок данных с отброшенной вспомогательной информацией - словарь, каждый ключ которого
            соответствует одной из таблиц с данными. Таблицы являются списками словарей, которые напрямую
            конвертируются в pandas.DataFrame.
        :raises ISSMoexError:
            Ошибка при обращении к ISS Moex.
        """
        url = self._url
        query = self._make_query(start)
        async with self._session.get(url, params=query) as respond:
            try:
                respond.raise_for_status()
            except client_exceptions.ClientResponseError:
                raise ISSMoexError("Неверный url", respond.url)
            else:
                raw_respond: List[Dict[str, Table]] = await respond.json()
                return raw_respond[1]

    async def get_all(self) -> TablesDict:
        """Собирает все блоки данных для запросов.

        :return:
            Объединенные из всех блоков данные с отброшенной вспомогательной информацией - словарь,
            каждый ключ которого соответствует одной из таблиц с данными. Таблицы являются списками
            словарей, которые напрямую конвертируются в pandas.DataFrame.
        """
        all_data: TablesDict = {}
        async for block in self:
            for table_name, table_rows in block.items():
                all_data.setdefault(table_name, []).extend(table_rows)
        return all_data

    def _make_query(self, start: Optional[int] = None) -> WebQuery:
        """Формирует параметры запроса.

        К общему набору параметров запроса добавляется требование предоставить ответ в виде
        расширенного json.
        """
        query: WebQuery = collections.ChainMap({}, BASE_QUERY, self._query)
        if start:
            query["start"] = start
        return query

    async def _iterator_maker(self) -> AsyncIterator[TablesDict]:
        start = 0
        while True:
            respond = await self.get(start)
            if (cursor_table := respond.get("history.cursor")) is not None:
                respond.pop("history.cursor")
                yield respond

                if not _cursor_has_more_data(start, cursor_table):
                    return
            else:
                yield respond

                table_name = next(iter(respond))
                block_size = len(respond[table_name])

                if not block_size:
                    return
                start += block_size
