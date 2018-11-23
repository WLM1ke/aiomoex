# Asyncio MOEX Informational & Statistical Server API 

[![Build Status](https://travis-ci.org/WLM1ke/aiomoex.svg?branch=master)](https://travis-ci.org/WLM1ke/aiomoex)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/363c10e1d85b404882326cf62b78f25c)](https://www.codacy.com/app/wlmike/aiomoex?utm_source=github.com&utm_medium=referral&utm_content=WLM1ke/aiomoex&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/363c10e1d85b404882326cf62b78f25c)](https://www.codacy.com/app/wlmike/aiomoex?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=WLM1ke/aiomoex&amp;utm_campaign=Badge_Grade)

Реализация на основе asyncio части  запросов к [MOEX Informational & Statistical Server](https://iss.moex.com/)

## Основные возможности
Реализован [клиент](https://github.com/WLM1ke/aiomoex/blob/master/aiomoex/client.py) с поддержкой запросов:
- С выдачей всей информации за раз
- С выдачей информации блоками с курсором
- С выдачей информации блоками без курсора

На его основе реализован ряд [запросов](https://github.com/WLM1ke/aiomoex/blob/master/aiomoex/requests.py) к MOEX ISS.
При необходимости список запросов может быть расширен:
- [Справочник](https://iss.moex.com/iss/reference/) запросов к MOEX ISS
- [Руководство разработчика](https://fs.moex.com/files/6523) с дополнительной информацией

## Начало работы
### Установка 
```
pip install amoex
```

### Пример использования реализованных запросов
История котировок SNGSP в режиме TQBR
```
import asyncio

import aiomoex
import pandas as pd


async def main():
    async with aiomoex.ISSClientSession():
        data = await aiomoex.get_board_history('SNGSP')
        df = pd.DataFrame(data)
        df.set_index('TRADEDATE', inplace=True)
        print(df.head(), '\n')
        print(df.tail(), '\n')
        df.info()


asyncio.run(main())
```
```
            CLOSE    VOLUME
TRADEDATE                  
2014-06-09  27.48  12674200
2014-06-10  27.55  14035900
2014-06-11  28.15  27208800
2014-06-16  28.27  68059900
2014-06-17  28.20  22101600 

             CLOSE    VOLUME
TRADEDATE                   
2018-11-16  37.860   9660800
2018-11-19  37.315  28765600
2018-11-20  36.790  19853500
2018-11-21  36.930  14583000
2018-11-22  37.480   9656600 

<class 'pandas.core.frame.DataFrame'>
Index: 1125 entries, 2014-06-09 to 2018-11-22
Data columns (total 2 columns):
CLOSE     1125 non-null float64
VOLUME    1125 non-null int64
dtypes: float64(1), int64(1)
memory usage: 26.4+ KB
```
### Пример реализации нового запроса
Перечень акций, торгующихся в режиме TQBR
```
import asyncio

from aiomoex import client
import pandas as pd


async def main():
    request_url = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
    arguments = {'securities.columns': 'SECID,REGNUMBER,LOTSIZE,SHORTNAME'}
    iss = client.ISSClient(request_url, arguments)
    iss.start_session()
    data = await iss.get()
    df = pd.DataFrame(data['securities'])
    df.set_index('SECID', inplace=True)
    print(df.head(), '\n')
    print(df.tail(), '\n')
    df.info()
    await iss.close_session()


asyncio.run(main())
```
```
       LOTSIZE     REGNUMBER   SHORTNAME
SECID                                   
ABRD        10  1-02-12500-A  АбрауДюрсо
AFKS       100  1-05-01669-A  Система ао
AFLT        10  1-01-00010-A    Аэрофлот
AGRO         1          None    AGRO-гдр
AKRN         1  1-03-00207-A       Акрон 

       LOTSIZE     REGNUMBER  SHORTNAME
SECID                                  
YRSBP      100  2-01-50099-A  ТНСэнЯр-п
ZILL         1  1-02-00036-A     ЗИЛ ао
ZMZN        10  1-01-00230-A     ЗМЗ-ао
ZMZNP      100  2-01-00230-A     ЗМЗ-ап
ZVEZ      1000  1-01-00169-D  ЗВЕЗДА ао 

<class 'pandas.core.frame.DataFrame'>
Index: 277 entries, ABRD to ZVEZ
Data columns (total 3 columns):
LOTSIZE      277 non-null int64
REGNUMBER    268 non-null object
SHORTNAME    277 non-null object
dtypes: int64(1), object(2)
memory usage: 8.7+ KB
```

