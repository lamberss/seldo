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
    
    def __init__(self):
        """Initialize the database object."""
        self.__dict__ = self.__shared_state
        self._refcount += 1
        
        self._config = core.config.Config()
        self._connection = None

        self.connect()


    def close(self):
        """Force the database to close (no effect if not connected)."""
        if self.is_connected():
            self._connection.close()
            self._connection = None


    def commit(self):
        """Force the transaction to commit (no effect if not connected)."""
        if self.is_connected():
            self._connection.commit()


    def connect(self):
        """Force the connection to the database (no effect if already
        connected).
        """
        if not self.is_connected():
            self._connection = sqlite3.connect(self._config['dbfile'])
            self._connection.execute('PRAGMA foreign_keys = ON')
            self._connection.commit()


    def execute(self, *args, **kwargs):
        """Execute an SQL statement, and return a cursor into the database.

        If the database is not connected, then this call will attempt to
        connect the database first.
        """
        self.connect()
        return self._connection.execute(*args, **kwargs)


    def is_connected(self):
        """Return True if the database is connected, otherwise return
        False.
        """
        if self._connection is None:
            return False
        else:
            return True


    def __del__(self):
        """Destroy this database object.  If this is the last one, close
        the connection to the database.
        """
        self._refcount -= 1

        if self._refcount <= 0:
            self.close()
            self._refcount = 0
