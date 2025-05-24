"""Асинхронный клиент для MOEX ISS."""

from collections.abc import AsyncIterable, AsyncIterator
from typing import cast

import aiohttp
from aiohttp import client_exceptions

Values = str | int | float
TableRow = dict[str, Values]
Table = list[TableRow]
TablesDict = dict[str, Table]
WebQuery = dict[str, str | int]


class ISSMoexError(Exception):
    """Ошибки во время обработки запросов."""


def _cursor_block_size(start: int, cursor_table: Table) -> int:
    cursor, *wrong_data = cursor_table

    if wrong_data or cast("int", cursor["INDEX"]) != start:
        raise ISSMoexError(f"Некорректные данные history.cursor: {cursor_table}")

    block_size = cast("int", cursor["PAGESIZE"])

    if start + block_size < cast("int", cursor["TOTAL"]):
        return block_size
    return 0


class ISSClient(AsyncIterable[TablesDict]):
    """Асинхронный клиент для MOEX ISS - может быть использован с async for.

    Загружает данные для простых ответов с помощью метода get. Для ответов состоящих из нескольких блоков
    поддерживается протокол асинхронного генератора отдельных блоков или метод get_all для их
    автоматического сбора.
    """

    _client_session = None

    def __init__(self, session: aiohttp.ClientSession, url: str, query: WebQuery | None = None) -> None:
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

    async def get(self, start: int | None = None) -> TablesDict:
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
            except client_exceptions.ClientResponseError as err:
                raise ISSMoexError("Неверный url", respond.url) from err
            else:
                raw_respond: list[dict[str, Table]] = await respond.json()
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

    def _make_query(self, start: int | None = None) -> WebQuery:
        """Формирует параметры запроса.

        К общему набору параметров запроса добавляется требование предоставить ответ в виде
        расширенного json.
        """
        query: WebQuery = {"iss.json": "extended", "iss.meta": "off"} | self._query
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

                block_size = _cursor_block_size(start, cursor_table)
            else:
                yield respond

                table_name = next(iter(respond))
                block_size = len(respond[table_name])

            if not block_size:
                return
            start += block_size
