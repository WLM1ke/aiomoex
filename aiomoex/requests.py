"""Реализация части запросов к MOEX ISS

При необходимости могут быть дополнены:
    Полный перечень запросов https://iss.moex.com/iss/reference/
    Дополнительное описание https://fs.moex.com/files/6523
"""
import contextlib
import sys

from . import client

__all__ = [
    "ISSClientSession",
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

if sys.version_info >= (3, 7):
    BaseClass = contextlib.AbstractAsyncContextManager
else:
    BaseClass = object


class ISSClientSession(BaseClass):
    """Менеджер сессий соединений с MOEX ISS

    Открывает сессию - возможно использование с async with для своевременного закрытия
    """

    def __init__(self):
        client.ISSClient.start_session()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    @staticmethod
    async def close():
        """Закрывает сессию"""
        await client.ISSClient.close_session()

    @property
    def closed(self):
        """Закрыта ли данная сессия"""
        return client.ISSClient.is_session_closed()


def _make_query(
    *, q=None, interval=None, start=None, end=None, table=None, columns=None
):
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
    query = dict()
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


def _get_table(data, table):
    """Извлекает конкретную таблицу из данных"""
    try:
        data = data[table]
    except KeyError:
        raise client.ISSMoexError(f"Отсутствует таблица {table} в данных")
    return data


async def _get_short_data(url, table, query=None):
    """Получить данные для запроса с выдачей всей информации за раз

    :param url:
        URL запроса
    :param query:
        Дополнительные параметры запроса - None, если нет параметров
    :param table:
        Таблица, которую нужно выбрать

    :return:
        Конкретная таблица из запроса
    """
    iss = client.ISSClient(url, query)
    data = await iss.get()
    return _get_table(data, table)


async def _get_long_data(url, table, query=None):
    """Получить данные для запроса, в котором информация выдается несколькими блоками

    :param url:
        URL запроса
    :param query:
        Дополнительные параметры запроса - None, если нет параметров
    :param table:
        Таблица, которую нужно выбрать

    :return:
        Конкретная таблица из запроса
    """
    iss = client.ISSClient(url, query)
    data = await iss.get_all()
    return _get_table(data, table)


async def get_reference(placeholder="boards"):
    """Получить перечень доступных значений плейсхолдера в адресе запроса

    Например в описание запроса https://iss.moex.com/iss/reference/32 присутствует следующий адрес
    /iss/engines/[engine]/markets/[market]/boards/[board]/securities с плейсхолдерами engines, markets и boards

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/28

    :param placeholder:
        Наименование плейсхолдера в адресе запроса: engines, markets, boards, boardgroups, durations, securitytypes,
        securitygroups, securitycollections

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = "https://iss.moex.com/iss/index.json"
    return await _get_short_data(url, placeholder)


async def find_securities(string: str, columns=("secid", "regnumber")):
    """Найти инструменты по части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации

    Один из вариантов использования - по регистрационному номеру узнать предыдущие тикеры эмитента, и с помощью
    нескольких запросов об истории котировок собрать длинную историю с использованием всех предыдущих тикеров

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/32

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
    return await _get_short_data(url, table, query)


async def get_market_candle_borders(security, market="shares", engine="stock"):
    """Получить таблицу интервалов доступных дат для свечей различного размера на рынке для всех режимов торгов

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/156

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
    return await _get_short_data(url, table)


async def get_board_candle_borders(
    security, board="TQBR", market="shares", engine="stock"
):
    """Получить таблицу интервалов доступных дат для свечей различного размера в указанном режиме торгов

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/48

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
    return await _get_short_data(url, table)


async def get_market_candles(
    security, interval=24, start=None, end=None, market="shares", engine="stock"
):
    """Получить свечи в формате HLOCV указанного инструмента на рынке для основного режима торгов за интервал дат

    Если торговля идет в нескольких основных режимах, то на один интервал времени может быть выдано несколько свечек -
    по свечке на каждый режим. Предположительно такая ситуация может произойти для свечек длиннее 1 дня

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/155

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
    url = f"https://iss.moex.com/iss/engines/{engine}/markets/{market}/securities/{security}/candles.json"
    table = "candles"
    query = _make_query(interval=interval, start=start, end=end)
    return await _get_long_data(url, table, query)


async def get_board_candles(
    security,
    interval=24,
    start=None,
    end=None,
    board="TQBR",
    market="shares",
    engine="stock",
):
    """Получить свечи в формате HLOCV указанного инструмента в указанном режиме торгов за интервал дат

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/46

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
    return await _get_long_data(url, table, query)


async def get_board_dates(board="TQBR", market="shares", engine="stock"):
    """Получить интервал дат, доступных в истории для рынка по заданному режиму торгов

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/26

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
    return await _get_short_data(url, table)


async def get_board_securities(
    table="securities",
    columns=("SECID", "REGNUMBER", "LOTSIZE", "SHORTNAME"),
    board="TQBR",
    market="shares",
    engine="stock",
):
    """Получить таблицу инструментов по режиму торгов со вспомогательной информацией

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/32

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
    return await _get_short_data(url, table, query)


async def get_market_history(
    security,
    start=None,
    end=None,
    columns=("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    market="shares",
    engine="stock",
):
    """Получить историю по одной бумаге на рынке для всех режимов торгов за интервал дат

    На одну дату может приходиться несколько значений, если торги шли в нескольких режимах

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/63

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
    url = f"https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities/{security}.json"
    table = "history"
    query = _make_query(start=start, end=end, table=table, columns=columns)
    return await _get_long_data(url, table, query)


async def get_board_history(
    security,
    start=None,
    end=None,
    columns=("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    board="TQBR",
    market="shares",
    engine="stock",
):
    """Получить историю торгов для указанной бумаги в указанном режиме торгов за указанный интервал дат

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/65

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
    return await _get_long_data(url, table, query)
