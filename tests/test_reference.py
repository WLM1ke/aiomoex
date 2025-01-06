import pytest

from aiomoex import reference


async def test_get_reference(http_session):
    data = await reference.get_reference(http_session, "engines")
    assert isinstance(data, list)
    assert len(data) == 11
    assert data[0] == {"id": 1, "name": "stock", "title": "Фондовый рынок и рынок депозитов"}


check_points = [
    ("1-02-65104-D", {"UPRO", "EONR", "OGK4"}),
    ("10301481B", {"SBER", "SBER03"}),
    ("20301481B", {"SBERP", "SBERP03"}),
    ("1-02-06556-A", {"PHOR"}),
]


@pytest.mark.parametrize(("reg_number", "expected"), check_points)
async def test_find_find_securities(http_session, reg_number, expected):
    data = await reference.find_securities(http_session, reg_number)
    assert isinstance(data, list)
    assert expected == {row["secid"] for row in data if row["regnumber"] == reg_number}
