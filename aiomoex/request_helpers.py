"""Вспомогательные функции для построения запросов."""
from typing import Final, Iterable, Optional

import aiohttp

from aiomoex import client

# Режимы по умолчанию для запросов
DEFAULT_ENGINE: Final = "stock"
DEFAULT_MARKET: Final = "shares"
DEFAULT_BOARD: Final = "TQBR"
# Ключивые плейсхолдеры и константы для запросов
SECURITIES: Final = "securities"
CANDLE_BORDERS: Final = "candleborders"
CANDLES: Final = "candles"


def make_url(
    *,
    history: Optional[bool] = None,
    engine: Optional[str] = None,
    market: Optional[str] = None,
    board: Optional[str] = None,
    security: Optional[str] = None,
    ending: Optional[str] = None,
) -> str:
    """Формирует URL для запроса."""
    url_parts = ["https://iss.moex.com/iss"]
    if history:
        url_parts.append("/history")
    if engine:
        url_parts.append(f"/engines/{engine}")
    if market:
        url_parts.append(f"/markets/{market}")
    if board:
        url_parts.append(f"/boards/{board}")
    if security:
        url_parts.append(f"/securities/{security}")
    if ending:
        url_parts.append(f"/{ending}")
    url_parts.append(".json")
    return "".join(url_parts)


def make_query(
    *,
    question: Optional[str] = None,
    interval: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    table: Optional[str] = None,
    columns: Optional[Iterable[str]] = None,
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
    if table:
        query["iss.only"] = f"{table},history.cursor"
    if columns:
        query[f"{table}.columns"] = ",".join(columns)
    return query


def get_table(table_dict: client.TablesDict, table_name: str) -> client.Table:
    """Извлекает конкретную таблицу из данных."""
    try:
        table = table_dict[table_name]
    except KeyError:
        raise client.ISSMoexError(f"Отсутствует таблица {table_name} в данных")
    return table


async def get_short_data(
    session: aiohttp.ClientSession, url: str, table_name: str, query: Optional[client.WebQuery] = None,
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
    session: aiohttp.ClientSession, url: str, table_name: str, query: Optional[client.WebQuery] = None,
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
