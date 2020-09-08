Asyncio MOEX ISS API
====================
.. image:: https://travis-ci.org/WLM1ke/aiomoex.svg?branch=master
    :target: https://travis-ci.org/WLM1ke/aiomoex
.. image:: https://api.codacy.com/project/badge/Coverage/363c10e1d85b404882326cf62b78f25c
    :target: https://www.codacy.com/app/wlmike/aiomoex?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=WLM1ke/aiomoex&amp;utm_campaign=Badge_Coverage
.. image:: https://badge.fury.io/py/aiomoex.svg
    :target: https://badge.fury.io/py/aiomoex

Реализация на основе asyncio части  запросов к `MOEX Informational & Statistical Server <https://www.moex.com/a2193>`_.

Документация
------------
https://wlm1ke.github.io/aiomoex/

Основные возможности
--------------------
Реализовано несколько функций-запросов информации о торгуемых акциях и их исторических котировках, результаты которых
напрямую конвертируются в pandas.DataFrame.

Работа функций базируется на универсальном клиенте, позволяющем осуществлять произвольные запросы к MOEX ISS, поэтому
перечень доступных функций-запросов может быть легко расширен. При необходимости добавления функций воспользуйтесь
`Issues <https://github.com/WLM1ke/aiomoex/issues>`_ на GitHub с указанием ссылки на описание запроса:

* Полный перечень возможных `запросов <https://iss.moex.com/iss/reference/>`_ к MOEX ISS
* Официальное `Руководство разработчика <https://fs.moex.com/files/6523>`_ с дополнительной информацией

Почему asyncio?
---------------
На многие запросы MOEX ISS выдает данные порциями по 100 элементов, и для получения всей информации требуются
дополнительные обращения к серверу для загрузки данных не с начальной позиции. Например, для скачивания котировок
всех акций во всех режимах может потребоваться несколько десятков тысяч обращений к серверу.

Результаты маленького тестирования загрузки исторических котировок в режиме TQBR для 35 и 277 (всех торгуемых) акций с
помощью синхронных запросов:

============== ============ ============
 Вид запросов   35 акций     277 акций
============== ============ ============
 asyncio        12.6 сек     40.6 сек
 Синхронные     210.4 сек    1436.9 сек
 Ускорение      16.7 раз     35.4 раза
============== ============ ============

Начало работы
=============
Установка
---------

.. code-block:: Bash

   $ pip install aiomoex

Пример использования реализованных запросов
-------------------------------------------
История котировок SNGSP в режиме TQBR::

    import asyncio

    import aiohttp

    import aiomoex
    import pandas as pd


    async def main():
        async with aiohttp.ClientSession() as session:
            data = await aiomoex.get_board_history(session, 'SNGSP')
            df = pd.DataFrame(data)
            df.set_index('TRADEDATE', inplace=True)
            print(df.head(), '\n')
            print(df.tail(), '\n')
            df.info()


    asyncio.run(main())

.. code-block::

               BOARDID  CLOSE    VOLUME         VALUE
    TRADEDATE
    2014-06-09    TQBR  27.48  12674200  3.484352e+08
    2014-06-10    TQBR  27.55  14035900  3.856417e+08
    2014-06-11    TQBR  28.15  27208800  7.602146e+08
    2014-06-16    TQBR  28.27  68059900  1.913160e+09
    2014-06-17    TQBR  28.20  22101600  6.292844e+08

               BOARDID   CLOSE    VOLUME         VALUE
    TRADEDATE
    2020-09-01    TQBR  37.245  15671200  5.824013e+08
    2020-09-02    TQBR  37.535  34659700  1.296441e+09
    2020-09-03    TQBR  36.955  28177000  1.049745e+09
    2020-09-04    TQBR  36.915  21908000  8.076767e+08
    2020-09-07    TQBR  37.200  13334400  4.955280e+08

    <class 'pandas.core.frame.DataFrame'>
    Index: 1573 entries, 2014-06-09 to 2020-09-07
    Data columns (total 4 columns):
     #   Column   Non-Null Count  Dtype
    ---  ------   --------------  -----
     0   BOARDID  1573 non-null   object
     1   CLOSE    1573 non-null   float64
     2   VOLUME   1573 non-null   int64
     3   VALUE    1573 non-null   float64
    dtypes: float64(2), int64(1), object(1)
    memory usage: 61.4+ KB

Пример реализации запроса с помощью клиента
-------------------------------------------
Перечень акций, торгующихся в режиме TQBR (`описание запроса <https://iss.moex.com/iss/reference/32>`_)::

    import asyncio

    import aiohttp

    import aiomoex
    import pandas as pd


    async def main():
        request_url = "https://iss.moex.com/iss/engines/stock/" "markets/shares/boards/TQBR/securities.json"
        arguments = {"securities.columns": ("SECID," "REGNUMBER," "LOTSIZE," "SHORTNAME")}

        async with aiohttp.ClientSession() as session:
            iss = aiomoex.ISSClient(session, request_url, arguments)
            data = await iss.get()
            df = pd.DataFrame(data["securities"])
            df.set_index("SECID", inplace=True)
            print(df.head(), "\n")
            print(df.tail(), "\n")
            df.info()


    asyncio.run(main())

.. code-block::

              REGNUMBER  LOTSIZE   SHORTNAME
    SECID
    ABRD   1-02-12500-A       10  АбрауДюрсо
    AFKS   1-05-01669-A      100  Система ао
    AFLT   1-01-00010-A       10    Аэрофлот
    AGRO           None        1    AGRO-гдр
    AKRN   1-03-00207-A        1       Акрон

              REGNUMBER  LOTSIZE   SHORTNAME
    SECID
    YNDX           None        1  Yandex clA
    YRSB   1-01-50099-A       10     ТНСэнЯр
    YRSBP  2-01-50099-A       10   ТНСэнЯр-п
    ZILL   1-02-00036-A        1      ЗИЛ ао
    ZVEZ   1-01-00169-D     1000   ЗВЕЗДА ао

    <class 'pandas.core.frame.DataFrame'>
    Index: 260 entries, ABRD to ZVEZ
    Data columns (total 3 columns):
     #   Column     Non-Null Count  Dtype
    ---  ------     --------------  -----
     0   REGNUMBER  248 non-null    object
     1   LOTSIZE    260 non-null    int64
     2   SHORTNAME  260 non-null    object
    dtypes: int64(1), object(2)
    memory usage: 8.1+ KB
