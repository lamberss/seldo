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

import unittest
import core.config
import core.db as db



class TestDB(unittest.TestCase):
    """Test the DB class."""
    
    def setUp(self):
        """Set up common test harness for this class."""
        self.config = core.config.Config()
        self.config['dbfile'] = ':memory:'
        self.db = db.DB()


    def tearDown(self):
        """Tear down the common test harness for this class."""
        self.config.reset()
        self.db.close()
        del self.db
        
    
    def test_00_init(self):
        """DB - initialized as database controller with open connection."""
        self.assertEqual(self.db.is_connected(), True)
        self.db.close()


    def test_01_del(self):
        """DB - closes the database on deletion."""
        d = db.DB()
        self.assertEqual(self.db.is_connected(), True)
        # Manually resetting the refcount to one so deleting "d" will result
        # in the class thinking all instances are deleted.
        d._refcount = 1
        del d
        self.assertEqual(self.db.is_connected(), False)


    def test_02_borg(self):
        """DB - follows the "borg" design pattern."""
        d = db.DB()
        d.execute('CREATE TABLE TestTable(name TEXT);')
        test_value = 'hi rory'
        d.execute('INSERT INTO TestTable(name) VALUES(?);', (test_value,))
        results = self.db.execute('SELECT * FROM TestTable;')
        self.assertEqual(results.fetchone()[0], test_value)


    def test_10_commit(self):
        """DB - commit raises no errors, even when not connected."""
        self.db.execute('CREATE TABLE TestTable(name TEXT);')
        self.db.execute('INSERT INTO TestTable(name) VALUES(?);', ('testval',))

        # Try committing, and assert that the commit did not raise an error
        self.db.commit()
        self.assertTrue(True)

        # Try committing, and assert that the commit did not raise an error
        self.db.close()
        self.db.commit()
        self.assertTrue(True)
