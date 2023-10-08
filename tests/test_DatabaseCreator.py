import pytest
from main import DatabaseCreator
from pathlib import Path


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

