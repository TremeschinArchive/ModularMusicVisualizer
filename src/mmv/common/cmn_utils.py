"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Set of utilities for micro managing stuff, also every function is
coded to be as safe as possible and assert common error edge cases

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""

import mmv.common.cmn_any_logger
from pathlib import Path
import subprocess
import hashlib
import logging
import random
import shutil
import toml
import glob
import math
import time
import uuid
import yaml
import sys
import os


class Utils:
    def __init__(self):
        self.os = self.get_os()

    # Convert to pathlib.Path
    def enforce_pathlib_Path(self, path):
        if isinstance(path, str): path = Path(path)
        return path

    def reset_dir(self, path: Path):
        debug_prefix = "[Utils.reset_dir]"
        logging.info(f"{debug_prefix} Reset directory (remove")
        assert path.is_dir, f"{debug_prefix} Path [{path}] must be directory"
        if os.path.exists(path): shutil.rmtree(path)
        path.mkdir(parents = True)

    # Copy every file of a directory to another
    # TODO: new code style
    def copy_files_recursive(self, src, dst):
        print(src, dst)
        if os.path.isdir(src) and os.path.isdir(dst) :
            for path in glob.glob(src + '/*.*'):
                if not any([f in path for f in os.listdir(dst)]):
                    print("Moving path [%s] --> [%s]" % (path, dst))
                    shutil.copy(path, dst)
                else:
                    pass
                    # print("File already under dst dir")
        else:
            print("src and dst must be dirs")
            sys.exit(-1)

    # Get the full path of a random file from a given directory
    def random_file_from_dir(self, path, silent = False):
        debug_prefix = "[Utils.random_file_from_dir]"

        # Log action
        if not silent:
            logging.debug(f"{debug_prefix} Get random file / name from path [{path}]")

        # Actually get the random file from the directory
        r = random.choice([f"{path}{os.path.sep}{name}" for name in os.listdir(path)])

        # Debug and return the path
        if not silent:
            logging.info(f"{debug_prefix} Got file [{r}], ")

        return r
    
    # The name says it all, given a path get all of its subdirectories
    # Returns empty list "None" --> [] if there is no directory
    def get_recursively_all_subdirectories(self, path, silent = False):
        debug_prefix = "[Utils.get_recursive_subdirectories]"

        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Get recursively all subdirectories of path [{path}]")

        # The subdirectories we find
        subdirectories = []

        # Walk on the path
        for root, directories, files in os.walk(path):
            
            # Append the root + subdir for every subdir (if there is any)
            for directory in directories:
                subdirectories.append(os.path.join(root, directory))
        
        # Hard debug
        if not silent:
            logging.debug(f"{debug_prefix} Return subdirectories {subdirectories}")

        return subdirectories

    # Get operating system we're running on
    # FIXME: Need testing / get edge cases like:
    # - Temple OS
    # - Solus (linux?)
    # - Haiku
    # - ReactOS (nt?)
    # - DOS (well you're probably not running this here)
    # - ChromeOS (linux?)
    # - *BSD (*nix -> posix -> linux?)
    def get_os(self):

        # Get the desired name from a dict matching against os.name
        return {
            "posix": "linux",
            "nt": "windows",
            "darwin": "macos"
        }.get(os.name)
    
    # Load a yaml and return its content
    def load_yaml(self, path, silent = False) -> None:
        debug_prefix = "[Utils.load_yaml]"
        
        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Loading YAML file from path [{path}], getting absolute realpath first")

        # Open file in read mode
        with open(path, "r") as f:
            data = yaml.load(f, Loader = yaml.FullLoader)

        # Log read data
        if not silent:
            logging.debug(f"{debug_prefix} Loaded data is: {data}")

        # Return the data
        return data
    
    # Save a dictionary to a YAML file, make sure the directory exists first..
    def dump_yaml(self, data, path, silent = False) -> None:
        debug_prefix = "[Utils.dump_yaml]"

        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Dumping some data to YAML located at: [{path}], getting absolute realpath first")
            logging.debug(f"{debug_prefix} Data being dumped: [{data}]")

        # Get absolute and realpath
        path = self.get_absolute_realpath(path, silent = True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style = False)

    # Load a toml and return its content
    def load_toml(self, path, silent = False) -> None:
        debug_prefix = "[Utils.load_toml]"

        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Loading TOML file from path [{path}], getting absolute realpath first")

        # Error assertion
        self.assert_file(path)

        # Open file in read mode
        with open(path, "r") as f:
            data= toml.loads(f.read())

        # Log read data
        if not silent:
            logging.debug(f"{debug_prefix} Loaded data is: {data}")

        # Return the data
        return data
    
    # Save a dictionary to a TOML file, make sure the directory exists first..
    def dump_toml(self, data, path, silent = False) -> None:
        debug_prefix = "[Utils.dump_toml]"

        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Dumping some data to TOML located at: [{path}], getting absolute realpath first")
            logging.debug(f"{debug_prefix} Data being dumped: [{data}]")

        # Make sure the parent path exists
        self.mkparent_dne(path)

        # Get absolute and realpath
        path = self.get_absolute_realpath(path, silent = True)

        with open(path, "w") as f:
            f.write(toml.dumps(data))

    # Waits until file exist
    def until_exist(self, path, silent = False) -> None:
        debug_prefix = "[Utils.until_exist]"

        # Log action
        if not silent:
            logging.warn(f"{debug_prefix} Waiting for file or diretory: [{path}]")

        while True:
            time.sleep(0.1)
            if os.path.exists(path):
                break

    # Check if either type A = wanted[0] and B = wanted[1] or the opposite
    def is_matching_type(self, items, wanted):
        # print("Checking items", items, "on wanted", wanted)
        for _, item in enumerate(items):
            for wanted_index, wanted_type in enumerate(wanted):
                if isinstance(item, wanted_type):
                    del wanted[wanted_index]
                    continue
                else:
                    return False
        return True

    # If name is an file on PATH marked as executable returns True
    def has_executable_with_name(self, binary, silent = False) -> None:
        debug_prefix = "[Utils.has_executable_with_name]"

        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Checking we can find the executable [{binary}] in PATH")

        # Tell if we can find the binary
        exists = shutil.which(binary) is not None

        # If it doesn't exist show warning, no need to quit
        if not silent:
            msg = f"{debug_prefix} Executable exists: [{exists}]"

            # Info if exists else warn
            if exists:
                logging.info(msg)
            else:
                logging.warn(msg)

        return exists
    
    # Get a executable from path, returns False if it doesn't exist
    def get_executable_with_name(self, binary, extra_paths = [], silent = False):
        debug_prefix = "[Utils.get_executable_with_name]"

        # Log action
        if not silent:
            logging.info(f"{debug_prefix} Get executable with name [{binary}]")

        # Force list variable
        extra_paths = self.force_list(extra_paths)
        search_path = os.environ["PATH"] + os.pathsep + os.pathsep.join([str(path) for path in extra_paths])

        # Log search paths
        if not silent:
            logging.debug(f"{debug_prefix} Extra paths to search: [{extra_paths}]")
            logging.debug(f"{debug_prefix} Full search path: [{search_path}]")

        # Locate it
        locate = shutil.which(binary, path = search_path)

        # If it's not found then return False
        if locate is None:
            if not silent:
                logging.warn(f"{debug_prefix} Couldn't find binary, returning False..")
            return False
            
        # Else return its path
        if not silent:
            logging.info(f"{debug_prefix} Binary found and located at [{locate}]")

        return locate
    
    # If data is string, "abc" -> ["abc"], if data is list, return data
    def force_list(self, data):
        if not isinstance(data, list):
            data = [data]
        return data

    # Get one (astronomically guaranteed) unique id, upper(uuid4)
    # purpose key is for logging messages so we identify which identifier is binded to what object
    def get_unique_id(self, purpose = "", silent = False) -> str:
        debug_prefix = "[Utils.get_unique_id]"

        # Get an uppercase uuid4
        unique_id = str(uuid.uuid4()).upper()[0:8]

        # Change the message based on if we have or have not a purpose
        if not silent:
            if purpose:
                message = f"{debug_prefix} Get unique identifier for [{purpose}]: [{unique_id}]"
            else:
                message = f"{debug_prefix} Get unique identifier: [{unique_id}]"

            # Log the message
            logging.info(message)

        return unique_id

    # "true" if True else "false"
    def bool_to_string(self, value): return "true" if value else "false"

# Utilities in processing dictionaries, lists
class DataUtils:
    
    # Get a "subdictionary" from the data dictionary where the keys range in between start and end
    def dictionary_items_in_between(self, data, start, end):
        return {k: v for k, v in data.items() if k > start and k < end}
    
    # Get a "subdictionary" from the data dictionary where the keys range in between start and end
    def list_items_in_between(self, data, start, end):
        return [x for x in data if ((start < x) and (x < end))]

    # Slice an array in (tries to) n equal slices
    def equal_slices(self, array, n):
        size = len(array)
        return [ array[i: min(i+n, size) ] for i in range(0, size, n) ]
    
    # Wrapper on a .get function for a list like we have in dicts: d.get(key, default)
    def list_get(self, l, index, default):
        try:
            return l[index]
        except IndexError:
            return default
        
    """
    Given a list of 2D, line intervals:

    [[1, 3], [4, 6], [5, 8], [8, 15], [9, 18], [10, 12], [10, 12], [10, 14], [12, 21], [12, 19]]

    There are a few overlaps like between [4, 6], [5, 8] and we want to sorten the first
    interval so it ends at the second's start --> [4, 5], [5, 8]

    There's also the case where you have multiple starting values:

    [10, 12], [10, 12], [10, 14]

    You wanna set it to the lowest and highest value, in this case, [10, 14]
    """
    def shorten_overlaps_keep_start_value(self, intervals: list) -> list:

        # Join multiple same start value intervals into the maximum one

        # Sort list by first item of lists
        intervals = sorted(intervals, key = lambda k: k[0])

        # Groups of value : values for every value
        groups = {}

        for item in intervals:

            # Add item[1] to each group item[0]
            if not item[0] in groups:
                groups[item[0]] = []

            # Add the value of this interval until value to groups
            groups[item[0]].append(item[1])

        # Reset L to this index : max(group[this index])
        # In case we have [10, 12] [10, 13] [10, 18] [10, 16],
        # it'll be {10: [12, 13, 18, 16]} and we set to [10, 18] because that's the max length
        intervals = [ [k, max(groups[k])] for k in groups.keys() ]
        
        # Check for actual overlaps 

        # List of index : new internal at that index
        patches = []

        # As we'll check every N with N+1, loop until N-1 so we don't get IndexError
        for n in range(len(intervals) - 1):

            # .. [4, 6] [5, 8] .. As you can see, the first list's second value
            # is greater than next list's first value, this is the next conditional
            if intervals[n][1] > intervals[n+1][0]:

                # The new interval we insert at that point will be starting at 
                # first list's start and ends on second's list start
                new_interval = [intervals[n][0], intervals[n+1][0]]

                # Add that patch
                patches.append([n, new_interval])
        
        # For not scrambling the indexes, we have to patch in reverse
        for n in reversed(patches):
            # Substitute the interval
            intervals[n[0]] = n[1]

        return intervals
    
