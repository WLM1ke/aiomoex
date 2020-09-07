"""Функции для получения информации о свечках."""
from typing import Optional

import aiohttp

from aiomoex import client, request_helpers
from aiomoex.request_helpers import (
    CANDLE_BORDERS,
    CANDLES,
    DEFAULT_BOARD,
    DEFAULT_ENGINE,
    DEFAULT_MARKET,
)


async def get_market_candle_borders(
    session: aiohttp.ClientSession,
    security: str,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить таблицу интервалов доступных дат для всех режимов торгов.

    Описание запроса - https://iss.moex.com/iss/reference/156

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги.
    :param market:
        Рынок - по умолчанию акции.
    :param engine:
        Движок - по умолчанию акции.

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame.
    """
    url = request_helpers.make_url(
        engine=engine, market=market, security=security, ending=CANDLE_BORDERS,
    )
    table = "borders"
    return await request_helpers.get_short_data(session, url, table)


async def get_board_candle_borders(
    session: aiohttp.ClientSession,
    security: str,
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить таблицу интервалов доступных дат для указанного режиме торгов.

    Описание запроса - https://iss.moex.com/iss/reference/48

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумагию
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2.
    :param market:
        Рынок - по умолчанию акции.
    :param engine:
        Движок - по умолчанию акции.

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = request_helpers.make_url(
        engine=engine, market=market, board=board, security=security, ending=CANDLE_BORDERS,
    )
    table = "borders"
    return await request_helpers.get_short_data(session, url, table)


async def get_market_candles(
    session: aiohttp.ClientSession,
    security: str,
    interval: int = 24,
    start: Optional[str] = None,
    end: Optional[str] = None,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить свечи в формате HLOCV указанного инструмента на рынке для основного режима торгов.

    Если торговля идет в нескольких основных режимах, то на один интервал времени может быть выдано
    несколько свечек - по свечке на каждый режим. Предположительно такая ситуация может произойти для
    свечек длиннее 1 дня.

    Описание запроса - https://iss.moex.com/iss/reference/155

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги.
    :param interval:
        Размер свечки - целое число 1 (1 минута), 10 (10 минут), 60 (1 час), 24 (1 день), 7 (1 неделя),
        31 (1 месяц) или 4 (1 квартал). По умолчанию дневные данные.
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории.
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории.
    :param market:
        Рынок - по умолчанию акции.
    :param engine:
        Движок - по умолчанию акции.

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame.
    """
    url = request_helpers.make_url(engine=engine, market=market, security=security, ending=CANDLES)
    table = CANDLES
    query = request_helpers.make_query(interval=interval, start=start, end=end)
    return await request_helpers.get_long_data(session, url, table, query)


async def get_board_candles(
    session: aiohttp.ClientSession,
    security: str,
    interval: int = 24,
    start: Optional[str] = None,
    end: Optional[str] = None,
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить свечи в формате HLOCV указанного инструмента в указанном режиме торгов за интервал дат.

    Описание запроса - https://iss.moex.com/iss/reference/46

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги.
    :param interval:
        Размер свечки - целое число 1 (1 минута), 10 (10 минут), 60 (1 час), 24 (1 день), 7 (1 неделя),
        31 (1 месяц) или 4 (1 квартал). По умолчанию дневные данные.
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории.
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории.
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2.
    :param market:
        Рынок - по умолчанию акции.
    :param engine:
        Движок - по умолчанию акции.

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame.
    """
    url = request_helpers.make_url(
        engine=engine, market=market, board=board, security=security, ending=CANDLES,
    )
    table = CANDLES
    query = request_helpers.make_query(interval=interval, start=start, end=end)
    return await request_helpers.get_long_data(session, url, table, query)
