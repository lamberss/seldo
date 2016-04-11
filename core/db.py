# Copyright 2016 Steven E. Lamberson, Jr. <steven.lamberson@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Handle interraction with the database.

This module provides a wrapper for database connections.
"""

import logging
import sqlite3

import core.config

class DB(object):
    """Consolidate database connections from all sources.

    This class creates objects that can interact with the database.  This
    class implements the "borg" design pattern, where every instance of the
    class is guaranteed to have the same state.  This ensures that the
    database is only connected to once.

    The class mainly exposes the "execute" method, which ensures that the
    connection is active and then calls the execute method on the connection.

    The database connected to is determined by the value of the "dbfile"
    entry in the configuration dictionary.
    """

    __shared_state = {'_refcount': 0}
    
    def __init__(self, initialize=True):
        """Initialize the database object."""
        self.__dict__ = self.__shared_state
        self._config = core.config.Config()
        self._log = logging.getLogger(__name__)
        self._log.addHandler(logging.NullHandler())
        
        self._db = sqlite3.connect(self._config['dbfile'])
        self._cursor = None

        if initialize:
            self._initialize()


    def add_tag(self, new_tag):
        """Add a tag to the Tags table, if it does not exist.  Return id of
        the tag created, or of the already existing tag if it already exists.
        """
        sql = 'INSERT INTO Tags(name) VALUES (?);'
        new_id = self._change([sql], [(new_tag,)])
        if new_id is None:
            result = self._query('SELECT id FROM Tags WHERE name=?', (new_tag,))
            new_id = result.fetchone()[0]
        return new_id


    def edit_tag(self, tag_id, new_tag_value):
        """Change the tag with id=tag_id to have the value new_tag_value."""
        sql = 'UPDATE Tags SET name=? WHERE id=?'
        self._change([sql], [(new_tag_value, tag_id)])


    def _change(self, sql_list, sql_params_list=None):
        """Execute the list of SQL statements, each intended to modify the
        database.  Return the id of the row created in the last statement,
        or return None if the last statement did not create a row.
        """
        result = None
        cur = self._db.cursor()
        try:
            if sql_params_list:
                for (sql, sql_params) in zip(sql_list, sql_params_list):
                    self._log.debug('SQL: {}'.format(sql))
                    if sql_params:
                        self._log.debug('SQL params: {}'.format(sql_params))
                    result = cur.execute(sql, sql_params)
            else:
                for sql in sql_list:
                    self._log.debug('SQL: {}'.format(sql))
                    result = cur.execute(sql)
            self._log.debug('Commit changes to database.')
            self._db.commit()
        except sqlite3.Error as e:
            self._log.error(e)
            self._log.debug('Rolling back database.')
            self._db.rollback()
        finally:
            cur.close()

        if result is not None:
            the_id = result.lastrowid
            result.close()
        else:
            the_id = None

        return the_id


    def _initialize(self):
        """Initialize the database schema."""
        sql = [
            "CREATE TABLE IF NOT EXISTS Tags(\n" + \
            "    id    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\n" + \
            "    name  TEXT UNIQUE NOT NULL\n" + \
            ");",
            "CREATE TABLE IF NOT EXISTS Tasks(\n" + \
            "    id       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,\n" + \
            "    name     TEXT NOT NULL,\n" + \
            "    created  DATETIME DEFAULT CURRENT_TIMESTAMP\n" + \
            ");"
        ]
        self._change(sql)


    def _query(self, sql, sql_params=None):
        """Execute the passed SQL statement."""
        self._cursor = self._db.cursor()
        if sql_params:
            self._log.debug('SQL: {}'.format(sql))
            self._log.debug('SQL params: {}'.format(sql_params))
            result = self._cursor.execute(sql, sql_params)
        else:
            self._log.debug('SQL: {}'.format(sql))
            result = self._cursor.execute(sql)
        return result
