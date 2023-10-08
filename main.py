import sqlite3
from tabulate import tabulate
from pathlib import Path


class DatabaseCreator:
    """
    A class for creating and managing SQLite3 database for a quiz application.
    """
    def __init__(self, path: Path):
        """
        Initialize the DatabaseCreator object.

        Creates a connection to the database and create the required tables.
        """
        self.path = path
        self.conn = None
        self.cursor = None

        self.create_tables_if_not_exist()

    def __enter__(self) -> "DatabaseCreator":
        """
        Enter the context and initialize the database connection and cursor.
        """
        self.initialize_database_connection_and_cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Close connection to the database.
        """
        self.disconnect_from_database()

    def initialize_database_connection(self) -> None:
        """
        Initialize a connection to the database.
        """
        self.conn = sqlite3.connect(self.path)

    def initialize_cursor(self) -> None:
        """
        Initialize a cursor to perform operation on the database.
        """
        self.cursor = self.conn.cursor()

    def initialize_database_connection_and_cursor(self) -> None:
        """
        Initialize a connection to the database and cursor to perform operation on the database.
        """
        self.initialize_database_connection()
        self.initialize_cursor()

    def disconnect_from_database(self) -> None:
        """
        Close connection to the database.
        """
        self.cursor.close()
        self.conn.close()
        self.cursor = None
        self.conn = None

    def execute_operation(self) -> None:
        """
        Commit changes to the database.
        """
        self.conn.commit()

    def create_tables_if_not_exist(self) -> None:
        """
        Create required tables if they do not exist.
        """
        with self:
            self.create_questions_table()
            self.create_answers_table()
            self.execute_operation()

    def create_questions_table(self) -> None:
        """
        Create "questions" table in database if it does not exit.
        The table contains columns "id" (primary key) and "question".
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS questions(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                question TEXT)""")

    def create_answers_table(self) -> None:
        """
        Create the "answers" table in the database if it does not exist.
        The table contains columns "id" (primary key), question_id (foreign key) related to the "questions" table,
        "answer_a" (correct answer), "answer_b", "answer_c" and "answer_d".
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS answers(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                question_id INTEGER UNIQUE NOT NULL,
                                answer_a TEXT NOT NULL,
                                answer_b TEXT NOT NULL,
                                answer_c TEXT NOT NULL,
                                answer_d TEXT NOT NULL,
                                FOREIGN KEY (question_id) REFERENCES questions(id))""")

    @staticmethod
    def confirm_user_action(message: str) -> bool:
        """
        Prompts the user for action confirmation.
        """
        while True:
            answer = input(message).lower().strip()
            if answer == "yes":
                return True
            elif answer == "no":
                return False
            else:
                print("Please answer 'Yes' or 'No'.")

    def add_data_to_questions_table(self, question_text: str) -> None:
        """
        Add a new question to the "questions" table.

        Usage:
        with DatabaseCreator(Path("database_path")) as db:
            db.add_data_to_question_table("What is Azure?")
        """

        self.cursor.execute("INSERT INTO questions (question) VALUES (?)", (question_text.strip(),))
        self.execute_operation()

    def add_data_to_answers_table(self, question_id: int, answers: list) -> None:
        """
        Add an answers to the "answers" table. Remember 1st answer should be correct!!

        Usage:
        with DatabaseCreator(Path("database_path")) as db:
            db.add_data_to_answers_table(1, ["cloud", "music player", "color", "food"]

        """
        if not isinstance(answers, list):
            raise ValueError("Answers must be provided as a list.")

        if len(answers) != 4:
            raise ValueError("Exactly 4 answers are required (answer_a, answer_b, answer_c, answer_d).")

        for i, answer in enumerate(answers):
            if not isinstance(answer, str):
                raise ValueError(f"Answer {1+i} is not a string: {answer}")

        self.cursor.execute("INSERT INTO answers (question_id, answer_a, answer_b, answer_c, answer_d)"
                            " VALUES (?, ?, ?, ?, ?)", (question_id, (answers[0].strip()),
                                                        (answers[1]).strip(), (answers[2]).strip(),
                                                        (answers[3]).strip()))

        self.execute_operation()

    def remove_rows_from_questions_table(self, question_id: int, answer_removed=False) -> None:
        """
        Remove question form "questions" table based on "question_id" as long with corresponding answers.

        Usage:
        with DatabaseCreator(Path("database_path")) as db:
            db.remove_rows_from_questions_table(5)
        """
        self.cursor.execute("DELETE FROM questions WHERE id=(?)", (question_id,))
        if not answer_removed:
            self.cursor.execute("DELETE FROM answers WHERE question_id=(?)", (question_id,))

        self.execute_operation()

    def remove_rows_from_answers_table(self, answer_id: int = None, question_id: int = None,
                                       question_removed: bool = False) -> None:
        """
        Remove answers from "answers" table based on "question_id" or "answer_id". Additionally, can remove
        corresponding question upon user request.

        Usage:
        with DatabaseCreator(Path("database_path")) as db:
            # remove an answer based on "answer_id"
            db.remove_rows_from_answer_table(answer_id=1)
            # remove an answer based on "question_id"
            db.remove_rows_from_answer_table(question_id=5)
        """
        if question_id:
            self.cursor.execute("DELETE FROM answers WHERE question_id=(?)", (question_id,))

        if answer_id:
            if not question_removed:
                self.cursor.execute("SELECT question_id FROM answers WHERE id=(?)", (answer_id,))
                question_id = self.cursor.fetchone()[0]
            self.cursor.execute("DELETE FROM answers WHERE id=(?)", (answer_id,))

        self.execute_operation()

        if not question_removed and self.confirm_user_action("Would you like remove corresponding question? Yes/No:"):
            self.remove_rows_from_questions_table(question_id, answer_removed=True)

    def update_questions_table(self, question_id: int, question: str) -> None:
        """
        Update questions table.

       Usage:
        with DatabaseCreator(Path("database_path")) as db:
            db.update_questions_table(1, "2+2=?")
        """
        self.cursor.execute(f"UPDATE questions "
                            "SET question = ? "
                            "WHERE id = ?", (question, question_id))

        self.execute_operation()

    def update_answers_table(self,  answer_id: int = None, question_id: int = None, answer_a: str = None,
                             answer_b: str = None, answer_c: str = None, answer_d: str = None,
                             query_parameter: str = 'id') -> None:
        """
        Update answers table base on 'id' or 'question_id'.

        Usage:
        with DatabaseCreator(Path("database_path")) as db:
            db.update_answers_table(question_id=2, answer_c="water", query_parameter="question_id")

        :param query_parameter: Acceptable values 'id' or 'question_id'
        """
        query_parameter = query_parameter.lower()
        if query_parameter not in ("id", "question_id"):
            raise ValueError(f"query_parameter must be 'id' or 'question_id'. If you like update answers tabel based "
                             "on answer id you can omit this parameter. Received: {query_parameter}")

        update_values = []
        if answer_a is not None:
            update_values.append(("answer_a", answer_a))
        if answer_b is not None:
            update_values.append(("answer_b", answer_b))
        if answer_c is not None:
            update_values.append(('answer_c', answer_c))
        if answer_d is not None:
            update_values.append(('answer_d', answer_d))

        if query_parameter == "id":
            if not update_values and question_id is None:
                raise ValueError("At least one field should be updated")
            if question_id is not None:
                update_values.insert(0, ("question_id", question_id))

            for column, new_value in update_values:
                self.cursor.execute(f"UPDATE answers "
                                    f"SET {column} = ?"
                                    f"WHERE id = ?", (new_value, answer_id))
        else:
            if answer_id is not None:
                raise ValueError("Cannot update answer id (primary key).")
            for column, new_value in update_values:
                self.cursor.execute(f"UPDATE answers "
                                    f"SET {column} = ?"
                                    f"WHERE question_id = ?", (new_value, question_id))

        self.execute_operation()

    def get_question(self, question_id: int) -> str:
        self.cursor.execute("SELECT question FROM questions WHERE id=?", (question_id,))
        question = self.cursor.fetone()
        return question[0]

    def get_answers(self, question_id: int) -> tuple:
        self.cursor.execute("SELECT answer_a, answer_b, answer_c, answer_d FROM answers WHERE question_id=?",
                            (question_id,))
        answers = self.cursor.fetone()
        return answers

    def display_table_content(self, table_name: str) -> str:
        """
        Display content of a table chosen by user.

        Usage:
        with DatabaseCreator(Path("database_path")) as db:
            db.display_table_content("questions")
        """
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        column_names = [column[1] for column in self.cursor.fetchall()]

        self.cursor.execute(f"SELECT * FROM {table_name}")
        rows = self.cursor.fetchall()

        table = tabulate(rows, headers=column_names, tablefmt="pretty")
        return table

    def clear_table(self, table_name: str) -> None:
        """
        Clear table.

        Usage:
        with DatabaseCreator(Path("database_path")) as db:
            db.clear_table("questions")

        :param table_name: "questions" or "answers"
        """
        self.cursor.execute(f"TRUNCATE TABLE {table_name}")
