import pytest

from aiomoex import client, request_helpers


def test_make_query_empty() -> None:
    query = request_helpers.make_query()
    assert query == {}


def test_make_query_full() -> None:
    query = request_helpers.make_query(start=1, end=2, table=3, columns=("4",))
    assert isinstance(query, dict)
    assert len(query) == 4
    assert query["from"] == 1
    assert query["till"] == 2
    assert query["iss.only"] == "3,history.cursor"
    assert query[f"{3}.columns"] == "4"


def test_make_query_many_columns() -> None:
    query = request_helpers.make_query(table=1, columns=("2", "3"))
    assert isinstance(query, dict)
    assert len(query) == 2
    assert query["iss.only"] == "1,history.cursor"
    assert query[f"{1}.columns"] == "2,3"


def test_get_table_notable() -> None:
    with pytest.raises(client.ISSMoexError) as error:
        request_helpers.get_table({"a": "b"}, "b")
    assert "Отсутствует таблица b в данных" in str(error.value)
