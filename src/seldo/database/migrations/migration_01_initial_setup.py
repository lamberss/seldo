"""Set up the initial database."""

import sqlite3
from typing import List, Union


def migrate(connection: sqlite3.Connection,
            current_migrations: Union[List[int], None] = None):
    connection.execute(
        'CREATE TABLE IF NOT EXISTS todos ('
        '    todo_id INTEGER PRIMARY KEY,'
        '    summary TEXT NOT NULL,'
        '    description TEXT,'
        '    created TEXT NOT NULL,'
        '    modified TEXT NOT NULL'
        ')')
