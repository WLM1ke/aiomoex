Asyncio MOEX ISS API
===================================================

.. image:: https://travis-ci.org/WLM1ke/aiomoex.svg?branch=master
    :target: https://travis-ci.org/WLM1ke/aiomoex
.. image:: https://api.codacy.com/project/badge/Coverage/363c10e1d85b404882326cf62b78f25c
   :target: https://www.codacy.com/app/wlmike/aiomoex?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=WLM1ke/aiomoex&amp;utm_campaign=Badge_Coverage
.. image:: https://api.codacy.com/project/badge/Grade/363c10e1d85b404882326cf62b78f25c
   :target: https://www.codacy.com/app/wlmike/aiomoex?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=WLM1ke/aiomoex&amp;utm_campaign=Badge_Grade

Реализация на основе asyncio части  запросов к `MOEX Informational & Statistical Server <https://www.moex.com/a2193>`_

Основные возможности
--------------------
Реализован `клиент <https://github.com/WLM1ke/aiomoex/blob/master/aiomoex/client.py>`_ с поддержкой запросов:

* С выдачей всей информации за раз
* С выдачей информации блоками с курсором
* С выдачей информации блоками без курсора

На его основе реализован ряд `запросов <https://github.com/WLM1ke/aiomoex/blob/master/aiomoex/requests.py>`_,
результаты которых напрямую конвертируются в pandas.DataFrame.

При необходимости список запросов может быть расширен:

* Полный перечень `запросов <https://iss.moex.com/iss/reference/>`_ запросов к MOEX ISS
* Официальное `Руководство разработчика <https://fs.moex.com/files/6523>`_ с дополнительной информацией


Оглавление
----------
.. toctree::
   :maxdepth: 2

   getting_started
   api
