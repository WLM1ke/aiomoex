"""Запросы к MOEX ISS и асинхронный клиент"""
from enum import Enum


class ISSQueries(Enum):
    """Запросы к MOEX ISS

    Реализована часть запросов, при необходимости могут быть дополненны:
        Полный перечень запросов https://iss.moex.com/iss/reference/
        Дополнительное описание https://fs.moex.com/files/6523
    """
    # https://iss.moex.com/iss/reference/5
    SEARCH_SECURITIES = 'https://iss.moex.com/iss/securities.json'
    # https://iss.moex.com/iss/reference/32
    GET_BOARD_SECURITIES = 'https://iss.moex.com/iss/engines/{engine}/markets/{market}/boards/{board}/securities.json'
    # https://iss.moex.com/iss/reference/63
    GET_MARKET_SECURITY_HISTORY = 'https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/securities.json'
    # https://iss.moex.com/iss/reference/26
    GET_BOARD_HISTORY_DATES = ('https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/'
                               'boards/{board}/dates.json')
    # https://iss.moex.com/iss/reference/65
    GET_BOARD_SECURITY_HISTORY = ('https://iss.moex.com/iss/history/engines/{engine}/markets/{market}/'
                                  'boards/{board}/securities/securities.json')

