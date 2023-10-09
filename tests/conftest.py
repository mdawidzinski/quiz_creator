import pytest
from pathlib import Path
from main import DatabaseCreator

path = Path("test.db")


@pytest.fixture()
def setup_database():
    with DatabaseCreator(path) as db:
        yield db


@pytest.fixture()
def setup_teardown_database():
    with DatabaseCreator(path) as db:
        yield db
        db.clear_table("questions")
        db.clear_table("answers")
