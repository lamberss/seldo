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

"""Code to test the db module."""

import logging
import unittest

import core.config
import core.db as db

#logging.basicConfig(level=logging.DEBUG)

class TestDBprivate(unittest.TestCase):
    """Test the private methods of the DB class."""
    
    def setUp(self):
        """Set up common test harness for this class."""
        self.config = core.config.Config()
        self.config['dbfile'] = ':memory:'
        self.db = db.DB(initialize=False)


    def tearDown(self):
        """Tear down the common test harness for this class."""
        self.config.reset()
        
    
    def test_00_init(self):
        """DB - initialized and connection established."""
        self.assertTrue(self.db._db is not None)
        # Do some SQL and make sure we don't get an error
        self.db._db.execute('CREATE TABLE TestTable(name TEXT);')
        self.assertTrue(True)


    def test_01__query(self):
        """DB - _query returns all the results."""

        # Setup some test data
        test_values = ['hi rory', 'bye amy']
        self.db._db.execute('CREATE TABLE TestTable(name TEXT);')
        for i in test_values:
            self.db._db.execute('INSERT INTO TestTable VALUES(?);', (i,))

        # Call _query
        results = self.db._query('SELECT * FROM TestTable;')
            
        # Check the values in the returned cursor
        for (row,value) in zip(results,test_values):
            self.assertEqual(row[0], value)

        # Call _query
        results = self.db._query('SELECT * FROM TestTable WHERE name=:n;',
                                 {'n': test_values[0]})
            
        # Check the values in the returned cursor
        for (row,value) in zip(results,test_values[0:1]):
            self.assertEqual(row[0], value)


    def test_02__change(self):
        """DB - _change alters the database when SQL is good."""
        test_values = ['hi rory', 'bye amy']
        sql_list = ['CREATE TABLE TestTable(name TEXT);']
        sql_params_list = [{}]
        for i in test_values:
            sql_list.append('INSERT INTO TestTable VALUES(?);')
            sql_params_list.append((i,))

        # Call _change
        result = self.db._change(sql_list, sql_params_list)
        self.assertEqual(result, 2)

        # Try adding more without using parameter substitution
        result = self.db._change(['INSERT INTO TestTable VALUES("who?");'])
        self.assertEqual(result, 3)


    def test_03__change_bad(self):
        """DB - _change rollsback when 1st statement is bad."""

        # Setup some test data
        test_values = ['hi rory', 'bye amy']
        sql_list = []
        sql_params_list = []
        for i in test_values:
            sql_list.append('INSERT INTO BadTable VALUES(?);')
            sql_params_list.append((i,))

        # Call _change
        result = self.db._change(sql_list, sql_params_list)

        # Check return value
        self.assertTrue(result is None)

        # Check database status
        result = self.db._query('SELECT name FROM sqlite_master WHERE ' +
                                'type="table" AND name="table_name";')
        self.assertEqual(len(result.fetchall()), 0)


    def test_04__change_rollback(self):
        """DB - _change rollsback when 2nd statement is bad."""

        # Setup some test data
        test_values = ['hi rory', 'bye amy']
        sql_list = ['CREATE TABLE TestTable(name TEXT);']
        for i in test_values:
            sql_list.append('INSERT INTO BadTable VALUES("{}");'.format(i))

        # Call _change
        result = self.db._change(sql_list)

        # Check return value
        self.assertTrue(result is None)

        # Check database status
        result = self.db._query('SELECT name FROM sqlite_master WHERE ' +
                                'type="table" AND name="table_name";')
        self.assertEqual(len(result.fetchall()), 0)


    def test_10__initialize(self):
        """DB - _initialize creates the correct database schema."""
        # Initialize the database
        self.db._initialize()
        
        # Check the list of created tables.
        tables = ['Tags', 'Tasks']
        result = self.db._query('SELECT name FROM sqlite_master ' +
                                'WHERE type="table" AND name NOT LIKE "sqlite%";')
        result_tables = []
        for r in result:
            result_tables.append(r[0])
        result_tables.sort()
        self.assertEqual(result_tables, tables)

        # Check the schema for each table.
        schema = {
            'Tags':
"""CREATE TABLE Tags(
    id    INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name  TEXT UNIQUE NOT NULL
)""",
            'Tasks':
"""CREATE TABLE Tasks(
    id       INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name     TEXT NOT NULL,
    created  DATETIME DEFAULT CURRENT_TIMESTAMP
)""",
        }
        for table in tables:
            result = self.db._query('SELECT sql FROM sqlite_master ' +
                                    'WHERE type="table" AND name=?;', (table,))
            sql = result.fetchone()[0]
            self.assertEqual(sql, schema[table])


            
class TestDBpublic(unittest.TestCase):
    """Test the public methods of the DB class."""
    
    def setUp(self):
        """Set up common test harness for this class."""
        self.config = core.config.Config()
        self.config['dbfile'] = ':memory:'
        self.db = db.DB()


    def tearDown(self):
        """Tear down the common test harness for this class."""
        self.config.reset()
        
    
    def test_add_tag(self):
        """DB - add_tag adds a tag."""
        result = self.db._query('SELECT id FROM Tags;')
        self.assertEqual(len(result.fetchall()), 0)
        new_id = self.db.add_tag("new tag")
        self.assertEqual(new_id, 1)
        result = self.db._query('SELECT id FROM Tags;')
        results = result.fetchall()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], new_id)
        
    
    def test_add_tag_already_exists(self):
        """DB - add_tag returns id of tag if already exists."""
        result = self.db._query('SELECT id FROM Tags;')
        self.assertEqual(len(result.fetchall()), 0)
        new_id = self.db.add_tag("new tag")
        new_id_second = self.db.add_tag("new tag")
        self.assertEqual(new_id, new_id_second)


    def test_edit_tag(self):
        """DB - edit_tag changes the name of a tag."""
        new_tag_text = "edited tag"
        the_id = self.db.add_tag("new  tag")
        self.db.edit_tag(the_id, new_tag_text)
        result = self.db._query('SELECT id FROM Tags WHERE name=?;',
                                (new_tag_text,))
        results = result.fetchall()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], the_id)
        
        
        
