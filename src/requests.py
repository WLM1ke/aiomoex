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
    """
    url = 'https://iss.moex.com/iss/securities.json'
    iss = client.ISSClient(url, dict(q=query))
    data = await iss.get()
    print(data.keys())
    return data['securities']


async def get_board_securities(table='securities', board='TQBR', market='shares', engine='stock'):
    """Получить таблицу инструментов по режиму торгов

    Описание запроса - https://iss.moex.com/iss/reference/32

    В ответе содержатся две таблицы:
        securities - справочник торгуемых ценных бумаг
        marketdata - данные результатми торгов текущего дня
    """
    url = f'https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities.json'
    iss = client.ISSClient(url)
    data = await iss.get()
    return data[table]


async def get_market_security_history(security, start=None, end=None, market='shares', engine='stock'):
    """Получить историю по одной бумаге на рынке за интервал дат

    Описание запроса - https://iss.moex.com/iss/reference/63

    start и end - дата в str вида ГГГГ-ММ-ДД. При отсутсвии данные будут загружены с начала и до конца
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
    return data['history']


async def get_index_history(index='MCFTRR', start=None, end=None):
    """Получить историю значений индекса за указанный интервал дат

    start и end - дата в str вида ГГГГ-ММ-ДД
    """
    return await get_board_security_history(index, start, end, 'RTSI', 'index')


if __name__ == '__main__':
    import asyncio

    async def run():
        print(pd.DataFrame(await get_index_history(start='2018-01-01')))

    asyncio.run(run())
