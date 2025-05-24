import pytest

from aiomoex import client, request_helpers


def test_make_url_empty() -> None:
    out = request_helpers.make_url()
    expect = "https://iss.moex.com/iss.json"

    assert out == expect


def test_make_url_full() -> None:
    out = request_helpers.make_url(
        prefix="prefix",
        engine="e",
        market="m",
        board="b",
        analytics="a",
        security="s",
        suffix="suffix",
    )
    expect = "https://iss.moex.com/iss/prefix/engines/e/markets/m/boards/b/analytics/a/securities/s/suffix.json"

    assert out == expect


def test_make_query_empty() -> None:
    query = request_helpers.make_query()
    assert query == {}


def test_make_query_full() -> None:
    query = request_helpers.make_query(
        question="q",
        interval=1,
        start="1",
        end="2",
        table="3",
        date="4",
        columns=("5",),
    )
    expected = {
        "q": "q",
        "interval": 1,
        "from": "1",
        "till": "2",
        "date": "4",
        "iss.only": "3,history.cursor",
        "3.columns": "5",
    }

    assert query == expected


def test_make_query_many_columns() -> None:
    query = request_helpers.make_query(table="1", columns=("2", "3"))
    assert isinstance(query, dict)
    assert len(query) == 2
    assert query["iss.only"] == "1,history.cursor"
    assert query[f"{1}.columns"] == "2,3"


def test_get_table_notable() -> None:
    with pytest.raises(client.ISSMoexError) as error:
        request_helpers.get_table({"a": "b"}, "b")
    assert "Отсутствует таблица b в данных" in str(error.value)
