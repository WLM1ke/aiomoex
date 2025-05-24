"""Реализация части запросов к MOEX ISS.

Результаты запросов являются списками словарей и могут быть конвертированы в pandas.DataFrame.

Работа функций-запросов базируется на универсальном клиенте, позволяющем осуществлять произвольные
запросы к ISS MOEX, поэтому перечень доступных функций-запросов может быть при необходимости дополнен:

- Полный перечень запросов https://iss.moex.com/iss/reference/
- Дополнительное описание https://fs.moex.com/files/6523
"""

from aiomoex.candles import (
    get_board_candle_borders,
    get_board_candles,
    get_market_candle_borders,
    get_market_candles,
)
from aiomoex.client import ISSClient, TableRow, TablesDict, Values
from aiomoex.history import get_board_dates, get_board_history, get_board_securities, get_market_history
from aiomoex.reference import find_securities, get_reference
from aiomoex.statistics import get_index_tickers

__all__ = [
    "ISSClient",
    "TableRow",
    "TablesDict",
    "Values",
    "find_securities",
    "get_board_candle_borders",
    "get_board_candles",
    "get_board_dates",
    "get_board_history",
    "get_board_securities",
    "get_index_tickers",
    "get_market_candle_borders",
    "get_market_candles",
    "get_market_history",
    "get_reference",
]
