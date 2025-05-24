"""Вспомогательные функции для построения запросов."""

from collections.abc import Iterable
from typing import Final

import aiohttp

from aiomoex import client

# Режимы по умолчанию для запросов
DEFAULT_ENGINE: Final = "stock"
DEFAULT_MARKET: Final = "shares"
INDEX_MARKET: Final = "index"
DEFAULT_BOARD: Final = "TQBR"
# Ключевые плейсхолдеры и константы для запросов
HISTORY: Final = "history"
STATISTICS: Final = "statistics"
SECURITIES: Final = "securities"
CANDLE_BORDERS: Final = "candleborders"
CANDLES: Final = "candles"
TICKERS: Final = "tickers"


def make_url(
    *,
    prefix: str | None = None,
    engine: str | None = None,
    market: str | None = None,
    board: str | None = None,
    analytics: str | None = None,
    security: str | None = None,
    suffix: str | None = None,
) -> str:
    """Формирует URL для запроса."""
    url_parts = ["https://iss.moex.com/iss"]
    if prefix:
        url_parts.append(f"/{prefix}")
    if engine:
        url_parts.append(f"/engines/{engine}")
    if market:
        url_parts.append(f"/markets/{market}")
    if board:
        url_parts.append(f"/boards/{board}")
    if analytics:
        url_parts.append(f"/analytics/{analytics}")
    if security:
        url_parts.append(f"/securities/{security}")
    if suffix:
        url_parts.append(f"/{suffix}")
    url_parts.append(".json")
    return "".join(url_parts)


def make_query(
    *,
    question: str | None = None,
    interval: int | None = None,
    start: str | None = None,
    end: str | None = None,
    date: str | None = None,
    table: str | None = None,
    columns: Iterable[str] | None = None,
) -> client.WebQuery:
    """Формирует дополнительные параметры запроса к MOEX ISS.

    :param question:
        Строка с частью характеристик бумаги для поиска.
    :param interval:
        Размер свечки.
    :param start:
        Начальная дата котировок.
    :param end:
        Конечная дата котировок.
    :param date:
        Дата, на которую нужно вывести информацию.
    :param table:
        Таблица, которую нужно загрузить (для запросов, предполагающих наличие нескольких таблиц).
    :param columns:
        Кортеж столбцов, которые нужно загрузить.

    :return:
        Словарь с дополнительными параметрами запроса.
    """
    query: client.WebQuery = {}
    if question:
        query["q"] = question
    if interval:
        query["interval"] = interval
    if start:
        query["from"] = start
    if end:
        query["till"] = end
    if date:
        query["date"] = date
    if table:
        query["iss.only"] = f"{table},history.cursor"
    if columns:
        query[f"{table}.columns"] = ",".join(columns)
    return query


def get_table(table_dict: client.TablesDict, table_name: str) -> client.Table:
    """Извлекает конкретную таблицу из данных."""
    try:
        table = table_dict[table_name]
    except KeyError as err:
        raise client.ISSMoexError(f"Отсутствует таблица {table_name} в данных") from err
    return table


async def get_short_data(
    session: aiohttp.ClientSession,
    url: str,
    table_name: str,
    query: client.WebQuery | None = None,
) -> client.Table:
    """Получить данные для запроса с выдачей всей информации за раз.

    :param session:
        Сессия http соединения.
    :param url:
        URL запроса.
    :param query:
        Дополнительные параметры запроса - None, если нет параметров.
    :param table_name:
        Таблица, которую нужно выбрать.

    :return:
        Конкретная таблица из запроса.
    """
    iss = client.ISSClient(session, url, query)
    table_dict = await iss.get()
    return get_table(table_dict, table_name)


async def get_long_data(
    session: aiohttp.ClientSession,
    url: str,
    table_name: str,
    query: client.WebQuery | None = None,
) -> client.Table:
    """Получить данные для запроса, в котором информация выдается несколькими блоками.

    :param session:
        Сессия http соединения.
    :param url:
        URL запроса.
    :param query:
        Дополнительные параметры запроса - None, если нет параметров.
    :param table_name:
        Таблица, которую нужно выбрать.

    :return:
        Конкретная таблица из запроса.
    """
    iss = client.ISSClient(session, url, query)
    table_dict = await iss.get_all()
    return get_table(table_dict, table_name)
