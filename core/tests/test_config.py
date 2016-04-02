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

"""Code to test the config module."""

import unittest
import core.config



class TestConfig(unittest.TestCase):
    """Test the Config class."""
    def tearDown(self):
        """Reset the configuration dictionary between calls."""
        a = core.config.Config()
        a.reset()
    
    
    def test_00_init(self):
        """Config - initialized as dict-like object with default values."""
        defaults = {'dbfile':'seldo.db'}
        config = core.config.Config()
        self.assertEqual(config, defaults)


    def test_01_borg(self):
        """Config - follows the "borg" design pattern."""
        a = core.config.Config()
        b = core.config.Config()
        a['setting 5'] = 37
        self.assertEqual(a, b)
        self.assertEqual(a['setting 5'], b['setting 5'])


    def test_02_dict(self):
        """Config - behaves like a "dict"."""
        a = core.config.Config()
        olen = len(a)
        a['setting 5'] = 37
        self.assertEqual(a['setting 5'], 37)
        self.assertEqual(len(a), olen+1)
        self.assertEqual(a.pop('setting 5'), 37)
        self.assertEqual(len(a), olen)
        with self.assertRaises(KeyError):
            b = a['setting 5']
        with self.assertRaises(KeyError):
            del a['setting 5']


    def test_05_reset(self):
        """Config - reset values to the default values."""
        a = core.config.Config()
        a.reset()
        def_value = a['dbfile']
        test_value = def_value + ':some_random_string'
        a['dbfile'] = test_value
        self.assertEqual(a['dbfile'], test_value)
        a.reset()
        self.assertEqual(a['dbfile'], def_value)


    def test_10_dict(self):
        """Config - default values do not override manually selected values."""
        a = core.config.Config()
        b = core.config.Config()
        test_value = a['dbfile'] + ':some_random_string'
        a['dbfile'] = test_value
        c = core.config.Config()
        self.assertEqual(a['dbfile'], test_value)
        self.assertEqual(b['dbfile'], test_value)
        self.assertEqual(c['dbfile'], test_value)
