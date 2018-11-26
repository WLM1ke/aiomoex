"""Реализация части запросов к MOEX ISS

При необходимости могут быть дополнены:
    Полный перечень запросов https://iss.moex.com/iss/reference/
    Дополнительное описание https://fs.moex.com/files/6523
"""
from . import client

__all__ = ['ISSClientSession',
           'get_reference',
           'find_securities',
           'get_market_candle_borders',
           'get_market_candles',
           'get_board_securities',
           'get_market_history',
           'get_board_history']


class ISSClientSession:
    """Менеджер сессий соединений с MOEX ISS

    Открывает сессию и поддерживает протокол асинхронного контекстного менеджера (async with)
    для своевременного закрытия
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


def _make_query(*, start=None, end=None, table=None, columns=None):
    """Формирует дополнительные параметры запроса к MOEX ISS

    В случае False значений не добавляются в запрос

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
    if start:
        query['from'] = start
    if end:
        query['till'] = end
    if table:
        query['iss.only'] = f'{table},history.cursor'
    if columns:
        query[f'{table}.columns'] = ','.join(columns)
    return query


async def get_reference(placeholder='boards'):
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
    url = 'https://iss.moex.com/iss/index.json'
    iss = client.ISSClient(url)
    data = await iss.get()
    return data[placeholder]


async def find_securities(sting: str, columns=('secid', 'regnumber')):
    """Найти инструменты по части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации

    Один из вариантов использования - по регистрационному номеру узнать предыдущие тикеры эмитента, и с помощью
    нескольких запросов об истории котировок собрать длинную историю с использованием всех предыдущих тикеров

    Для работы требуется открытая ISSClientSession

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param sting:
        Часть Кода, Названия, ISIN, Идентификатора Эмитента, Номера гос.регистрации
    :param columns:
        Кортеж столбцов, которые нужно загрузить - по умолчанию тикер и номер государственно регистрации.
        Если пустой или None, то загружаются все столбцы

    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = 'https://iss.moex.com/iss/securities.json'
    table = 'securities'
    query = _make_query(table=table, columns=columns)
    query['q'] = sting
    iss = client.ISSClient(url, query)
    data = await iss.get()
    return data[table]


async def get_market_candle_borders(security, market='shares', engine='stock'):
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
    url = f'https://iss.moex.com/iss/engines/{engine}/markets/{market}/securities/{security}/candleborders.json'
    table = 'borders'
    iss = client.ISSClient(url)
    data = await iss.get()
    return data[table]


async def get_market_candles(security, interval=24, start=None, end=None, market='shares', engine='stock'):
    """Получить свечи в формате HLOCV указанного инструмента на рынке для всех режимов торгов за интервал дат

    Если торговля идет в нескольких режимах, то на один интервал времени может быть выдано несколько свечек - по свечке
    на каждый режим

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
    url = f'https://iss.moex.com/iss/engines/{engine}/markets/{market}/securities/{security}/candles.json'
    table = 'candles'
    query = _make_query(start=start, end=end)
    query['interval'] = interval
    iss = client.ISSClient(url, query)
    data = await iss.get_all()
    return data[table]


async def get_board_securities(table='securities', columns=('SECID', 'REGNUMBER', 'LOTSIZE', 'SHORTNAME'),
                               board='TQBR', market='shares', engine='stock'):
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
    url = f'https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities.json'
    query = _make_query(table=table, columns=columns)
    iss = client.ISSClient(url, query)
    data = await iss.get()
    return data[table]


async def _get_history(url, start, end, columns):
    """Осуществляет запрос характерный для раздела history MOEX ISS

    :param url:
        Адрес запроса из раздела history
    :param start:
        Начальная дата котировок
    :param end:
        Конечная дата котировок
    :param columns:
        Кортеж столбцов, которые нужно загрузить

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    table = 'history'
    query = _make_query(start=start, end=end, table=table, columns=columns)
    iss = client.ISSClient(url, query)
    tables = await iss.get_all()
    try:
        data = tables[table]
    except KeyError:
        raise client.ISSMoexError(f'Отсутствуют исторические котировки для {url}')
    return data


async def get_market_history(security, start=None, end=None, columns=('BOARDID', 'TRADEDATE', 'CLOSE', 'VOLUME'),
                             market='shares', engine='stock'):
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
        Кортеж столбцов, которые нужно загрузить - по умолчанию дата торгов, цена закрытия и объем. Если
        пустой или None, то загружаются все столбцы
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = f'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities/{security}.json'
    data = await _get_history(url, start, end, columns)
    return data


async def get_board_history(security, start=None, end=None, columns=('TRADEDATE', 'CLOSE', 'VOLUME'),
                            board='TQBR', market='shares', engine='stock'):
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
        Кортеж столбцов, которые нужно загрузить - по умолчанию дата торгов, цена закрытия и объем. Если
        пустой или None, то загружаются все столбцы
    :param board:
        Режим торгов - по умолчанию основной режим торгов T+2
    :param market:
        Рынок - по умолчанию акции
    :param engine:
        Движок - по умолчанию акции

    :return:
        Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (f'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/'
           f'boards/{board}/securities/{security}.json')
    data = await _get_history(url, start, end, columns)
    return data
