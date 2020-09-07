"""Реализация части запросов к MOEX ISS

При необходимости могут быть дополнены:
    Полный перечень запросов https://iss.moex.com/iss/reference/
    Дополнительное описание https://fs.moex.com/files/6523
"""
from typing import Iterable, Optional

import aiohttp

__all__ = [
    "get_reference",
    "find_securities",
    "get_market_candle_borders",
    "get_board_candle_borders",
    "get_market_candles",
    "get_board_candles",
    "get_board_dates",
    "get_board_securities",
    "get_market_history",
    "get_board_history",
]

from aiomoex import client


def _make_query(
    *,
    q: Optional[str] = None,
    interval: Optional[int] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    table: Optional[str] = None,
    columns: Optional[Iterable[str]] = None,
) -> client.WebQuery:
    """Формирует дополнительные параметры запроса к MOEX ISS

    В случае False значений не добавляются в запрос

    :param q:
        Строка с частью характеристик бумаги для поиска
    :param interval:
        Размер свечки
    :param start:
        Начальная дата котировок
    :param end:
        Конечная дата котировок
    :param table:
        Таблица, которую нужно загрузить (для запросов, предполагающих наличие нескольких таблиц)
    :param columns:
        Кортеж столбцов, которые нужно загрузить

    :return:
        Словарь с дополнительными параметрами запроса
    """
    query: client.WebQuery = dict()
    if q:
        query["q"] = q
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


def _get_table(data: client.TablesDict, table_name: str) -> client.Table:
    """Извлекает конкретную таблицу из данных"""
    try:
        table = data[table_name]
    except KeyError:
        raise client.ISSMoexError(f"Отсутствует таблица {table_name} в данных")
    return table


async def _get_short_data(
    session: aiohttp.ClientSession, url: str, table_name: str, query: Optional[client.WebQuery] = None,
) -> client.Table:
    """Получить данные для запроса с выдачей всей информации за раз

    :param session:
        Сессия http соединения.
    :param url:
        URL запроса
    :param query:
        Дополнительные параметры запроса - None, если нет параметров
    :param table_name:
        Таблица, которую нужно выбрать

    :return:
        Конкретная таблица из запроса
    """
    iss = client.ISSClient(session, url, query)
    data = await iss.get()
    return _get_table(data, table_name)


async def _get_long_data(
    session: aiohttp.ClientSession, url: str, table_name: str, query: Optional[client.WebQuery] = None,
) -> client.Table:
    """Получить данные для запроса, в котором информация выдается несколькими блоками

    :param session:
        Сессия http соединения.
    :param url:
        URL запроса
    :param query:
        Дополнительные параметры запроса - None, если нет параметров
    :param table_name:
        Таблица, которую нужно выбрать

    :return:
        Конкретная таблица из запроса
    """
    iss = client.ISSClient(session, url, query)
    data = await iss.get_all()
    return _get_table(data, table_name)


async def get_reference(session: aiohttp.ClientSession, placeholder: str = "boards") -> client.Table:
    """Получить перечень доступных значений плейсхолдера в адресе запроса

    Например в описание запроса https://iss.moex.com/iss/reference/32 присутствует следующий адрес
    /iss/engines/[engine]/markets/[market]/boards/[board]/securities с плейсхолдерами engines, markets и boards

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/28

    :param session:
        Сессия http соединения.
    :param placeholder:
        Наименование плейсхолдера в адресе запроса: engines, markets, boards, boardgroups, durations, securitytypes,
        securitygroups, securitycollections

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = "https://iss.moex.com/iss/index.json"
    return await _get_short_data(session, url, placeholder)


async def find_securities(
    session: aiohttp.ClientSession,
    string: str,
    columns: Optional[Iterable[str]] = ("secid", "regnumber"),
) -> client.Table:
    """Найти инструменты по части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации

    Один из вариантов использования - по регистрационному номеру узнать предыдущие тикеры эмитента, и с помощью
    нескольких запросов об истории котировок собрать длинную историю с использованием всех предыдущих тикеров

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param session:
        Сессия http соединения.
    :param string:
        Часть Кода, Названия, ISIN, Идентификатора Эмитента, Номера гос.регистрации
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию тикер и номер государственно регистрации.
        Если пустой или None, то загружаются все столбцы

    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = "https://iss.moex.com/iss/securities.json"
    table = "securities"
    query = _make_query(q=string, table=table, columns=columns)
    return await _get_short_data(session, url, table, query)


async def get_market_candle_borders(
    session: aiohttp.ClientSession, security: str, market: str = "shares", engine: str = "stock",
) -> client.Table:
    """Получить таблицу интервалов доступных дат для свечей различного размера на рынке для всех режимов торгов

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/156

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/securities/{security}/candleborders.json"
    table = "borders"
    return await _get_short_data(session, url, table)


async def get_board_candle_borders(
    session: aiohttp.ClientSession,
    security: str,
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
) -> client.Table:
    """Получить таблицу интервалов доступных дат для свечей различного размера в указанном режиме торгов

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/48

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (
        f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/"
        f"boards/{board}/securities/{security}/candleborders.json"
    )
    table = "borders"
    return await _get_short_data(session, url, table)


async def get_market_candles(
    session: aiohttp.ClientSession,
    security: str,
    interval: int = 24,
    start: Optional[str] = None,
    end: Optional[str] = None,
    market: str = "shares",
    engine: str = "stock",
) -> client.Table:
    """Получить свечи в формате HLOCV указанного инструмента на рынке для основного режима торгов за интервал дат

    Если торговля идет в нескольких основных режимах, то на один интервал времени может быть выдано несколько свечек -
    по свечке на каждый режим. Предположительно такая ситуация может произойти для свечек длиннее 1 дня

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/155

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги
    :param interval:
        Размер свечки - целое число 1 (1 минута), 10 (10 минут), 60 (1 час), 24 (1 день), 7 (1 неделя), 31 (1 месяц) или
        4 (1 квартал). По умолчанию дневные данные
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (
        f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/securities/{security}/candles.json"
    )
    table = "candles"
    query = _make_query(interval=interval, start=start, end=end)
    return await _get_long_data(session, url, table, query)


async def get_board_candles(
    session: aiohttp.ClientSession,
    security: str,
    interval: int = 24,
    start: Optional[str] = None,
    end: Optional[str] = None,
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
) -> client.Table:
    """Получить свечи в формате HLOCV указанного инструмента в указанном режиме торгов за интервал дат

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/46

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги
    :param interval:
        Размер свечки - целое число 1 (1 минута), 10 (10 минут), 60 (1 час), 24 (1 день), 7 (1 неделя), 31 (1 месяц) или
        4 (1 квартал). По умолчанию дневные данные
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (
        f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/"
        f"boards/{board}/securities/{security}/candles.json"
    )
    table = "candles"
    query = _make_query(interval=interval, start=start, end=end)
    return await _get_long_data(session, url, table, query)


async def get_board_dates(
    session: aiohttp.ClientSession, board: str = "TQBR", market: str = "shares", engine: str = "stock",
) -> client.Table:
    """Получить интервал дат, доступных в истории для рынка по заданному режиму торгов

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/26

    :param session:
        Сессия http соединения.
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список из одного элемента - словаря с ключами 'from' и 'till'
    """
    url = f"https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/boards/{board}/dates.json"
    table = "dates"
    return await _get_short_data(session, url, table)


async def get_board_securities(
    session: aiohttp.ClientSession,
    table: str = "securities",
    columns: Optional[Iterable[str]] = ("SECID", "REGNUMBER", "LOTSIZE", "SHORTNAME"),
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
) -> client.Table:
    """Получить таблицу инструментов по режиму торгов со вспомогательной информацией

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param session:
        Сессия http соединения.
    :param table:
        Таблица с данными, которую нужно вернуть: securities - справочник торгуемых ценных бумаг, marketdata -
        данные с результатами торгов текущего дня
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию тикер, номер государственно регистрации,
        размер лота и краткое название. Если пустой или None, то загружаются все столбцы
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities.json"
    query = _make_query(table=table, columns=columns)
    return await _get_short_data(session, url, table, query)


async def get_market_history(
    session: aiohttp.ClientSession,
    security: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    columns: Optional[Iterable[str]] = ("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    market: str = "shares",
    engine: str = "stock",
) -> client.Table:
    """Получить историю по одной бумаге на рынке для всех режимов торгов за интервал дат

    На одну дату может приходиться несколько значений, если торги шли в нескольких режимах

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/63

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию режим торгов, дата торгов, цена закрытия и объем в
        штуках и стоимости. Если пустой или None, то загружаются все столбцы
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (
        f"https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities/{security}.json"
    )
    table = "history"
    query = _make_query(start=start, end=end, table=table, columns=columns)
    return await _get_long_data(session, url, table, query)


async def get_board_history(
    session: aiohttp.ClientSession,
    security: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    columns: Optional[Iterable[str]] = ("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    board: str = "TQBR",
    market: str = "shares",
    engine: str = "stock",
) -> client.Table:
    """Получить историю торгов для указанной бумаги в указанном режиме торгов за указанный интервал дат

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/65

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию режим торгов, дата торгов, цена закрытия и объем в
        штуках и стоимости. Если пустой или None, то загружаются все столбцы
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (
        f"https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/"
        f"boards/{board}/securities/{security}.json"
    )
    table = "history"
    query = _make_query(start=start, end=end, table=table, columns=columns)
    return await _get_long_data(session, url, table, query)
