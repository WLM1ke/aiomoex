"""Реализация части запросов к MOEX ISS


При необходимости могут быть дополненны:
    Полный перечень запросов https://iss.moex.com/iss/reference/
    Дополнительное описание https://fs.moex.com/files/6523
"""
import client
import pandas as pd


async def find_securities(query: str):
    """Поиск инструмента по части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param query: Части Кода, Названию, ISIN, Идентификатору Эмитента, Номеру гос.регистрации
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = 'https://iss.moex.com/iss/securities.json'
    iss = client.ISSClient(url, dict(q=query))
    data = await iss.get()
    print(data.keys())
    return data['securities']


async def get_board_securities(table='securities', board='TQBR', market='shares', engine='stock'):
    """Получить таблицу инструментов по режиму торгов

    Описание запроса - https://iss.moex.com/iss/reference/32

    :param table: Таблица с данными, которую нужно вернуть: securities - справочник торгуемых ценных бумаг, marketdata -
    данные с результатами торгов текущего дня
    :param board: Режим торгов - по умолчанию основной режим торгов T+2
    :param market: Рынок - по умолчанию акции
    :param engine: Движок - по умолчанию акции
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = f'https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities.json'
    iss = client.ISSClient(url)
    data = await iss.get()
    return data[table]


async def get_market_security_history(security, start=None, end=None, market='shares', engine='stock'):
    """Получить историю по одной бумаге на рынке за интервал дат

    Описание запроса - https://iss.moex.com/iss/reference/63

    :param security: тикер ценной бумаги
    :param start: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала итории
    :param end: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены до конца истории
    :param market: Рынок - по умолчанию акции
    :param engine: Движок - по умолчанию акции
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = f'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities/{security}.json'
    query = dict()
    if start:
        query['from'] = start
    if end:
        query['till'] = end
    iss = client.ISSClient(url, query)
    data = await iss.get_all()
    return data['history']


async def get_board_security_history(security, start=None, end=None, board='TQBR', market='shares', engine='stock'):
    """Получить историю торгов для указанной бумаги на указанном режиме торгов за указанный интервал дат

    Описание запроса - https://iss.moex.com/iss/reference/65

    start и end - дата в str вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала и до конца


    :param security: тикер ценной бумаги
    :param start: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала итории
    :param end: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены до конца истории
    :param board: Режим торгов - по умолчанию основной режим торгов T+2
    :param market: Рынок - по умолчанию акции
    :param engine: Движок - по умолчанию акции
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    url = (f'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/'
           f'boards/{board}/securities/{security}.json')
    query = dict()
    if start:
        query['from'] = start
    if end:
        query['till'] = end
    iss = client.ISSClient(url, query)
    data = await iss.get_all()
    try:
        return data['history']
    except KeyError:
        raise client.ISSMoexError(f'Отсутсвует история для {security}')


async def get_index_history(start=None, end=None):
    """Получить историю значений Индекса полной доходности «нетто» (по налоговым ставкам российских организаций) за
    указанный интервал дат

    :param start: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала итории
    :param end: дата вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены до конца истории
    :return: Список словарей, которые напрямую конвертируется в pandas.DataFrame
    """
    return await get_board_security_history('MCFTRR', start, end, 'RTSI', 'index')
