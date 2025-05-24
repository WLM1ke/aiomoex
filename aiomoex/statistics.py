"""Функции для получения данных статистических данных по торгам."""

import aiohttp

from aiomoex import client, request_helpers
from aiomoex.request_helpers import DEFAULT_ENGINE, INDEX_MARKET, STATISTICS, TICKERS


async def get_index_tickers(
    session: aiohttp.ClientSession,
    index: str,
    date: str | None = None,
) -> client.Table:
    """Получить список тикеров входивших в индекс за все время торгов.

    Описание запроса - https://iss.moex.com/iss/reference/148

    :param session:
        Сессия http соединения.
    :param index:
        Индекс, для которого нужно запросить информацию.
    :param date:
        Дата, по которой нужно запросить информацию. Если не указано, то выводится информация за все время.

    :return:
        Список словарей с тикерами и интервалами дат, когда они были в составе индекса.
    """
    url = request_helpers.make_url(
        prefix=STATISTICS,
        engine=DEFAULT_ENGINE,
        market=INDEX_MARKET,
        analytics=index,
        suffix=TICKERS,
    )
    query = request_helpers.make_query(date=date)
    return await request_helpers.get_short_data(session, url, TICKERS, query)
