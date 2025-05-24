"""Функции для получения данных об исторических дневных котировках."""

from collections.abc import Iterable

import aiohttp

from aiomoex import client, request_helpers
from aiomoex.request_helpers import DEFAULT_BOARD, DEFAULT_ENGINE, DEFAULT_MARKET, SUFFIX_SECURITIES


async def get_board_dates(
    session: aiohttp.ClientSession,
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить интервал дат, доступных в истории для рынка по заданному режиму торгов.

    Описание запроса - https://iss.moex.com/iss/reference/26

    :param session:
        Сессия http соединения.
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2.
    :param market:
        Рынок - по умолчанию акции.
    :param engine:
        Движок - по умолчанию акции.

    :return:
        Список из одного элемента - словаря с ключами 'from' и 'till'.
    """
    url = request_helpers.make_url(
        prefix=request_helpers.PREFIX_HISTORY,
        engine=engine,
        market=market,
        board=board,
        suffix="dates",
    )
    table = "dates"
    return await request_helpers.get_short_data(session, url, table)


async def get_board_securities(
    session: aiohttp.ClientSession,
    table: str = SUFFIX_SECURITIES,
    columns: Iterable[str] | None = ("SECID", "REGNUMBER", "LOTSIZE", "SHORTNAME"),
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить таблицу инструментов по режиму торгов со вспомогательной информацией.

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param session:
        Сессия http соединения.
    :param table:
        Таблица с данными, которую нужно вернуть: securities - справочник торгуемых ценных бумаг,
        marketdata - данные с результатами торгов текущего дня.
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию тикер, номер государственно регистрации,
        размер лота и краткое название. Если пустой или None, то загружаются все столбцы.
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2.
    :param market:
        Рынок - по умолчанию акции.
    :param engine:
        Движок - по умолчанию акции.

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = request_helpers.make_url(engine=engine, market=market, board=board, suffix=SUFFIX_SECURITIES)
    query = request_helpers.make_query(table=table, columns=columns)
    return await request_helpers.get_short_data(session, url, table, query)


async def get_market_history(
    session: aiohttp.ClientSession,
    security: str,
    start: str | None = None,
    end: str | None = None,
    columns: Iterable[str] | None = ("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить историю по одной бумаге на рынке для всех режимов торгов за интервал дат.

    На одну дату может приходиться несколько значений, если торги шли в нескольких режимах.

    Описание запроса - https://iss.moex.com/iss/reference/63

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги.
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории.
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории.
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию режим торгов, дата торгов, цена закрытия
        и объем в штуках и стоимости. Если пустой или None, то загружаются все столбцы.
    :param market:
        Рынок - по умолчанию акции.
    :param engine:
        Движок - по умолчанию акции.

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame.
    """
    url = request_helpers.make_url(
        prefix=request_helpers.PREFIX_HISTORY, engine=engine, market=market, security=security
    )
    table = "history"
    query = request_helpers.make_query(start=start, end=end, table=table, columns=columns)
    return await request_helpers.get_long_data(session, url, table, query)


async def get_board_history(
    session: aiohttp.ClientSession,
    security: str,
    start: str | None = None,
    end: str | None = None,
    columns: Iterable[str] | None = ("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Получить историю торгов для указанной бумаги в указанном режиме торгов за указанный интервал дат.

    Описание запроса - https://iss.moex.com/iss/reference/65

    :param session:
        Сессия http соединения.
    :param security:
        Тикер ценной бумаги.
    :param start:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены с начала истории.
    :param end:
        Дата вида ГГГГ-ММ-ДД. При отсутствии данные будут загружены до конца истории.
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию режим торгов, дата торгов, цена закрытия
        и объем в штуках и стоимости. Если пустой или None, то загружаются все столбцы.
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
        prefix=request_helpers.PREFIX_HISTORY,
        engine=engine,
        market=market,
        board=board,
        security=security,
    )
    table = "history"
    query = request_helpers.make_query(start=start, end=end, table=table, columns=columns)
    return await request_helpers.get_long_data(session, url, table, query)
