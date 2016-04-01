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

"""Handle configuration input from the user.

This module provides code to handle configuration input from the user.
This includes environment variables, command line arugments, and
configuration files.
"""

import collections
import os

class Config(collections.MutableMapping):
    """Consolidate configuration input from all sources.

    This class creates objects that contain all the configuration input
    from all the sources (default values, configuration file, command-
    line arguments, and environment variables), ensuring the appropriate
    priority is given to the different inputs.

    This class implements the "borg" design pattern, where every instance
    of the class is guaranteed to have the same state.

    This class should be treated by client code as a "dict"-like object,
    where the keys are the configuration variable names and the values
    are the value of that configuration option.

    For example:

        config_object = Config()
        if config_object['verbose']:
            print("Verbose output is turned on.")
    """

    __shared_state = {}
    
    def __init__(self):
        """Initialize the configuration dictionary object."""
        self.__dict__ = self.__shared_state
        self._config = {}


    def __delitem__(self, key):
        """Delete key from the configuration dictionary. Raises KeyError if
        key is not in the configuration dictionary."""
        del self._config[key]


    def __getitem__(self, key):
        """Return the item in the configuration dictionary associated with
        the key.  Raises KeyError if key is not in the configuration
        dictionary.
        """
        return self._config[key]


    def __iter__(self):
        """Return an iterator over the keys in the configuration dictionary."""
        return iter(self._config)


    def __len__(self):
        """Return the number of items in the configuration dictionary."""
        return len(self._config)


    def __setitem__(self, key, value):
        """Associate value with the key in the configuration dictionary."""
        self._config[key] = value
