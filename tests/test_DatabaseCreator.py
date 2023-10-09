import pytest
from main import DatabaseCreator
from pathlib import Path

expected_columns = {
    "questions": ["id", "question"],
    "answers": ["id", "question_id", "answer_a", "answer_b", "answer_c", "answer_d"],
}

questions = ["question", "question1"]

questions_id = [1, 2]
answers = [["1", "2", "3", "4"], ["a", "b", "c", "d"]]


def test_context_manager() -> None:
    """
    Test if context manager works as intended.
    """
    try:
        with DatabaseCreator(Path("test.db")) as db:
            assert db.cursor is not None, "Cursor does not exist."
            assert db.conn is not None, "Connection to database did not open."
    except Exception as e:
        raise AssertionError(f"Error occurred inside with block{e}")
    else:
        assert db.cursor is None, "Cursor still active."
        assert db.conn is None, "Connection still open."


@pytest.mark.parametrize("table_name", expected_columns.keys())
def test_table_creation(setup_database: DatabaseCreator, table_name: str) -> None:
    """
    Smoke test to check if the tables are created within with statement.
    """
    setup_database.cursor.execute(f"SELECT * FROM {table_name}")
    table = setup_database.cursor.fetchall()
    assert table is not None, f"Couldn't create {table_name} table"


@pytest.mark.parametrize("table_name, table_columns", expected_columns.items())
def test_table_schema(setup_database: DatabaseCreator, table_name: str, table_columns: list):
    """
    Test if the tables columns have proper names.
    """
    try:
        setup_database.cursor.execute(f'PRAGMA table_info({table_name})')
        columns_info = setup_database.cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        assert column_names == table_columns, f'Columns name does not match for table {table_name}'
    except Exception as e:
        raise AssertionError(e)


@pytest.mark.parametrize("table_name", expected_columns)
def test_table_clearing(setup_database: DatabaseCreator, table_name: str) -> None:
    """
    Test if 'clear_table' method works properly.
    """
    if table_name == "questions":
        value = questions[0]
        setup_database.cursor.execute(f"INSERT INTO {table_name} (question) VALUES (?)", (value,))
        setup_database.execute_operation()
    if table_name == "answers":
        val = [questions_id[1]] + answers[0]
        value = tuple(val)
        setup_database.cursor.execute(f"INSERT INTO {table_name} (question_id, answer_a, answer_b, answer_c, answer_d)"
                              f"VALUES (?, ?, ?, ?, ?)", value)
        setup_database.execute_operation()

    setup_database.clear_table(table_name)
    setup_database.cursor.execute(f"SELECT * FROM {table_name}")
    table = setup_database.cursor.fetchall()
    assert table is not None, f"Table {table_name} is not empty. Got {table}"

