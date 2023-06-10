import sqlite3

from selutil.database import get_tables

from seldo.database.migrations import migration_01_initial_setup as migration


def test_add_todo():
    conn = sqlite3.connect(':memory:')
    with conn:
        migration.migrate(conn)
    with conn:
        conn.execute('INSERT INTO todos(summary, created, modified) '
                     'VALUES(?,?,?)', ('test todo 1', 'now', 'now'))
    with conn:
        conn.row_factory = sqlite3.Row
        result = conn.execute('SELECT * FROM todos')
    assert (dict(result.fetchone()) == {'todo_id': 1, 'summary': 'test todo 1',
                                        'description': None, 'created': 'now',
                                        'modified': 'now'})


def test_tables():
    conn = sqlite3.connect(':memory:')
    with conn:
        migration.migrate(conn)
    assert (get_tables(conn) == ['todos'])
