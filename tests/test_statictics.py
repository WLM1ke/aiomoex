import aiomoex


async def test_get_board_securities(http_session) -> None:
    out = await aiomoex.get_index_tickers(
        http_session,
        "MOEXTL",
        date="2025-05-23",
    )
    expected = [
        {"ticker": "MGTSP", "from": "2025-05-23", "till": "2025-05-23", "tradingsession": 3},
        {"ticker": "MTSS", "from": "2025-05-23", "till": "2025-05-23", "tradingsession": 3},
        {"ticker": "RTKM", "from": "2025-05-23", "till": "2025-05-23", "tradingsession": 3},
        {"ticker": "RTKMP", "from": "2025-05-23", "till": "2025-05-23", "tradingsession": 3},
    ]

    assert out == expected
