"""Функции для получения справочной информации."""

from collections.abc import Iterable

import aiohttp

from aiomoex import client, request_helpers
from aiomoex.request_helpers import SECURITIES


async def get_reference(session: aiohttp.ClientSession, placeholder: str = "boards") -> client.Table:
    """Получить перечень доступных значений плейсхолдера в адресе запроса.

    Например в описание запроса https://iss.moex.com/iss/reference/32 присутствует следующий адрес
    /iss/engines/[engine]/markets/[market]/boards/[board]/securities с плейсхолдерами engines, markets и
    boards.

    Описание запроса - https://iss.moex.com/iss/reference/28

    :param session:
        Сессия http соединения.
    :param placeholder:
        Наименование плейсхолдера в адресе запроса: engines, markets, boards, boardgroups, durations,
        securitytypes, securitygroups, securitycollections.

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame.
    """
    url = request_helpers.make_url(ending="index")
    return await request_helpers.get_short_data(session, url, placeholder)


async def find_securities(
    session: aiohttp.ClientSession,
    string: str,
    columns: Iterable[str] | None = ("secid", "regnumber"),
) -> client.Table:
    """Найти инструменты по части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации.

    Один из вариантов использования - по регистрационному номеру узнать предыдущие тикеры эмитента, и с
    помощью нескольких запросов об истории котировок собрать длинную историю с использованием всех
    предыдущих тикеров.

    Описание запроса - https://iss.moex.com/iss/reference/5

    :param session:
        Сессия http соединения.
    :param string:
        Часть Кода, Названия, ISIN, Идентификатора Эмитента, Номера гос.регистрации.
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию тикер и номер государственно регистрации.
        Если пустой или None, то загружаются все столбцы.

    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame.
    """
    url = request_helpers.make_url(ending=SECURITIES)
    table = SECURITIES
    query = request_helpers.make_query(question=string, table=table, columns=columns)
    return await request_helpers.get_short_data(session, url, table, query)
