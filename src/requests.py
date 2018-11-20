"""Реализация части запросов к MOEX ISS

При необходимости могут быть дополненны:
    Полный перечень запросов https://iss.moex.com/iss/reference/
    Дополнительное описание https://fs.moex.com/files/6523
"""
import client


def _make_query(*, start=None, end=None, table=None, columns=None):
    """Формирует дополнительные параметры запроса к MOEX ISS

    В случае False значений не добавляются в запрос

    :param start: Начальная дата котировок
    :param end: Конечная дата котировок
    :param table: Таблица, которую нужно загрузить (для запросов, предполагающих наличие нескольких таблиц)
    :param columns: Кортеж столбцов, которые нужно загрузить
    :return: Словарь с доплнительными параметрами запроса
    """
    query = dict()
    if start:
        query['from'] = start
    if end:
        query['till'] = end
    if table:
        query['iss.only'] = table
    if columns:
        query[f'{table}.columns'] = ','.join(columns)
    return query


async def find_securities(sting: str, columns=('secid', 'regnumber')):
    """Поиск инструмента по части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param sting: Части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации
    :param columns: Кортеж столбцов, которые нужно загрузить - по умолчанию тикер и номер государственно регистрации.
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


async def get_board_securities(table='securities', columns=('SECID', 'REGNUMBER', 'LOTSIZE', 'SHORTNAME'),
                               board='TQBR', market='shares', engine='stock'):
    """Получить таблицу инструментов по режиму торгов

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param table: Таблица с данными, которую нужно вернуть: securities - справочник торгуемых ценных бумаг, marketdata -
    данные с результатами торгов текущего дня
    :param columns: Кортеж столбцов, которые нужно загрузить - по умолчанию тикер, номер государственно регистрации,
    размер лота и краткое название. Если пустой или None, то загружаются все столбцы
    :param board: Режим торгов - по умолчанию основной режим торгов T+2
    :param market: Рынок - по умолчанию акции
    :param engine: Движок - по умолчанию акции
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = f'https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities.json'
    query = _make_query(table=table, columns=columns)
    iss = client.ISSClient(url, query)
    data = await iss.get()
    return data[table]


async def get_market_security_history(security, start=None, end=None, columns=('TRADEDATE', 'CLOSE', 'VOLUME'),
                                      market='shares', engine='stock'):
    """Получить историю по одной бумаге на рынке за интервал дат

    Описание запроса - https://iss.moex.com/iss/reference/63

    :param security: тикер ценной бумаги
    :param start: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала итории
    :param end: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены до конца истории
    :param columns: Кортеж столбцов, которые нужно загрузить - по умолчанию дата торгов, цена закрытия и объем. Если
    пустой или None, то загружаются все столбцы
    :param market: Рынок - по умолчанию акции
    :param engine: Движок - по умолчанию акции
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = f'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities/{security}.json'
    table = 'history'
    query = _make_query(start=start, end=end, table=table, columns=columns)
    query['iss.only'] = f'{table},history.cursor'
    iss = client.ISSClient(url, query)
    data = await iss.get_all()
    return data[table]


async def get_board_security_history(security, start=None, end=None, columns=('TRADEDATE', 'CLOSE', 'VOLUME'),
                                     board='TQBR', market='shares', engine='stock'):
    """Получить историю торгов для указанной бумаги на указанном режиме торгов за указанный интервал дат

    Описание запроса - https://iss.moex.com/iss/reference/65

    :param security: тикер ценной бумаги
    :param start: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала итории
    :param end: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены до конца истории
    :param columns: Кортеж столбцов, которые нужно загрузить - по умолчанию дата торгов, цена закрытия и объем. Если
    пустой или None, то загружаются все столбцы
    :param board: Режим торгов - по умолчанию основной режим торгов T+2
    :param market: Рынок - по умолчанию акции
    :param engine: Движок - по умолчанию акции
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (f'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/'
           f'boards/{board}/securities/{security}.json')
    table = 'history'
    query = _make_query(start=start, end=end, table=table, columns=columns)
    iss = client.ISSClient(url, query)
    data = await iss.get_all()
    try:
        return data['history']
    except KeyError:
        raise client.ISSMoexError(f'Отсутсвует история для {security}')


async def get_index_history(start=None, end=None, columns=('TRADEDATE', 'CLOSE'),):
    """Получить историю значений Индекса полной доходности «нетто» (по налоговым ставкам российских организаций) за
    указанный интервал дат

    :param start: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала итории
    :param end: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены до конца истории
    :param columns: Кортеж столбцов, которые нужно загрузить - по умолчанию дата торгов и цена закрытия. Если пустой или
    None, то загружаются все столбцы
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    return await get_board_security_history('MCFTRR', start, end, columns, 'RTSI', 'index')
