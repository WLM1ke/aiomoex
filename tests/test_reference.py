import pytest

from aiomoex import reference


@pytest.mark.asyncio
async def test_get_reference(http_session):
    data = await reference.get_reference(http_session, "engines")
    assert isinstance(data, list)
    assert len(data) == 7
    assert data == [
        {"id": 1, "name": "stock", "title": "Фондовый рынок и рынок депозитов"},
        {"id": 2, "name": "state", "title": "Рынок ГЦБ (размещение)"},
        {"id": 3, "name": "currency", "title": "Валютный рынок"},
        {"id": 4, "name": "futures", "title": "Срочный рынок"},
        {"id": 5, "name": "commodity", "title": "Товарный рынок"},
        {"id": 6, "name": "interventions", "title": "Товарные интервенции"},
        {"id": 7, "name": "offboard", "title": "ОТС-система"},
    ]


check_points = [
    ("1-02-65104-D", {"UPRO", "EONR", "OGK4"}),
    ("10301481B", {"SBER", "SBER03"}),
    ("20301481B", {"SBERP", "SBERP03"}),
    ("1-02-06556-A", {"PHOR"}),
]


@pytest.mark.parametrize("reg_number, expected", check_points)
@pytest.mark.asyncio
async def test_find_find_securities(http_session, reg_number, expected):
    data = await reference.find_securities(http_session, reg_number)
    assert isinstance(data, list)
    assert expected == {row["secid"] for row in data if row["regnumber"] == reg_number}
