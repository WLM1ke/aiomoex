"""Реализовано несколько функций-запросов информации о торгуемых акциях и их исторических котировках, результаты которых
напрямую конвертируются в pandas.DataFrame.

Работа функций базируется на универсальном клиенте, позволяющем осуществлять произвольные запросы к MOEX ISS, поэтому
перечень доступных функций-запросов может быть легко расширен.
"""
# noinspection PyUnresolvedReferences
from .requests import *
# noinspection PyUnresolvedReferences
from .client import ISSClient

__version__ = '1.1.0'
