"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
import mmv.common.cmn_any_logger
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

    # Make sure given path is a directory
    def assert_dir(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.assert_dir]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Making sure path [{path}] is a directory")

        # Error assertion

        correct = os.path.isdir(path)
        exists = os.path.exists(path)
        
        if not (exists and correct):
            err = f"{depth}{debug_prefix} [ERROR] Path exists: [{exists}], correct type (dir): [{correct}]"
            logging.error(err)
            raise RuntimeError(err)
    
    # Make sure given path is a file
    def assert_file(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.assert_file]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Making sure path [{path}] is a file")

        # Error assertion

        correct = os.path.isfile(path)
        exists = os.path.exists(path)
        
        if not (exists and correct):
            err = f"{depth}{debug_prefix} [ERROR] Path exists: [{exists}], correct type (file): [{correct}]"
            logging.error(err)
            raise RuntimeError(err)
 
    # Make directory / directories if it does not exist
    # Returns:
    # - True: existed before
    # - False: didn't existed before
    def mkdir_dne(self, path, depth = LOG_NO_DEPTH, silent = False) -> bool:
        debug_prefix = "[Utils.mkdir_dne]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Make directory if doesn't exist on path: [{path}], getting absolute and realpath first")

        # Get the absolute and realpath of it
        path = self.get_abspath(path = path, depth = ndepth, silent = silent)

        # Log the absolute and realpath we got
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Got absolute and realpath: [{path}]")

        # If path already exists, checks if it is in fact a directory otherwise something is wrong
        if os.path.exists(path):
            if not silent:
                logging.debug(f"{depth}{debug_prefix} Path already existed, checking if it's a file for error assertion..")
            
            # If path is a directory then something is wrong
            if os.path.isfile(path):
                logging.error(f"{depth}{debug_prefix} Path already existed and is a file, this function creates directories so for safety we'll quit as this is technically not intended behavior (mkdir on a file location, that means we probably misspelled something and created a file where we should in fact have a directory)")
                sys.exit(-1)
            
            # Return True - target already existed
            return True
            
        # Make the directory
        os.makedirs(path)

        # Check we created the path
        if not os.path.isdir(path):
            logging.error(f"{depth}{debug_prefix} Target path didn't exist and Python's os.makedirs() function couldn't create the directory (should be some sort of permission errors on Windows os? If we're here then only other option is the path naming is just wrong but os.makedirs would error out on its own")
            sys.exit(-1)

        # Return False - target didn't existed
        return False
    
    # Make file it does not exist
    # Returns:
    # - True: existed before
    # - False: didn't existed before
    def mkfile_dne(self, path, depth = LOG_NO_DEPTH, silent = False) -> bool:
        debug_prefix = "[Utils.mkfile_dne]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Make empty if doesn't exist on path: [{path}], getting absolute and realpath first")

        # Get the absolute and realpath of it
        path = self.get_abspath(path = path, depth = ndepth, silent = silent)

        # Log the absolute and realpath we got
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Got absolute and realpath: [{path}]")

        # If path already exists, checks if it is in fact a directory otherwise something is wrong
        if os.path.exists(path):
            if not silent:
                logging.debug(f"{depth}{debug_prefix} Path already existed, checking if it's a directory for error assertion..")

            # If path is a directory then something is wrong
            if os.path.isdir(path):
                logging.error(f"{depth}{debug_prefix} Path already existed and is a file, this function creates directories so for safety we'll quit as this is technically not intended behavior (mkdir on a file location, that means we probably misspelled something and created a file where we should in fact have a directory)")
                sys.exit(-1)

            # # Reset file content

            if not silent:
                logging.warn(f"{depth}{debug_prefix} Resetting file content [{path}]")

            with open(path, "w") as f:
                f.write("")

            return False
        return True
    
    # Make sure a parent directory exists
    def mkparent_dne(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.mkparent_dne]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Make sure the parent directory of the path [{path}] exists")

        # Get the absolute and real path of the parent dir
        abspath_realpath_parent_dir = self.get_path_parent_dir(
                self.get_abspath(
                    path, depth = ndepth + (2*LOG_NEXT_DEPTH), silent = silent
            ), depth = ndepth + LOG_NEXT_DEPTH, silent = silent
        )

        # Make it
        self.mkdir_dne(abspath_realpath_parent_dir, depth = ndepth, silent = silent)

        if not silent:
            logging.debug(f"{depth}{debug_prefix} (Parent) Directory guaranteed to exist [{abspath_realpath_parent_dir}]")

    # Deletes an directory, fail safe? Quits if we can't delete it..
    def rmdir(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.rmdir]"
        ndepth = depth + LOG_NEXT_DEPTH

        # If the asked directory is even a path
        if os.path.isdir(path):

            # Log action
            if not silent:
                logging.info(f"{depth}{debug_prefix} Removing dir: [{path}]")

            # Try removing with ignoring errors first..?
            shutil.rmtree(path, ignore_errors = True)

            # Not deleted? 
            if os.path.isdir(path):

                # Ok. We can't be silent here we're about to error out probably
                logging.warn(f"{depth}{debug_prefix} Error removing directory with ignore_errors=True, trying again.. will quit if we can't")

                # Remove without ignoring errors?
                shutil.rmtree(path, ignore_errors = False)

                # Still exists? oops, better quit
                if os.path.isdir(path):
                    logging.error(f"{depth}{debug_prefix} COULD NOT REMOVE DIRECTORY: [{path}]")
                    sys.exit(-1)

            # Warn we're done
            if not silent:
                logging.debug(f"{depth}{debug_prefix} Removed directory successfully")
        else:
            # Directory didn't exist at first, nothing to do here
            if not silent:
                logging.debug(f"{depth}{debug_prefix} Directory doesn't exists, nothing to do here... [{path}]")

    # Reset an file to empty contents
    def reset_file(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.reset_file]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Reset file located at: [{path}]")

        # Error assertion
        if (not os.path.isfile(path)) and (os.path.exists(path)):
            logging.error(f"{depth}{debug_prefix} [ERROR] Path is not a file: [{path}]")
            sys.exit(-1)
        
        # Write nothing on the file with write + override mode
        with open(path, "w") as f:
            f.write("")

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
    def random_file_from_dir(self, path, depth = LOG_NO_DEPTH, silent = False):
        debug_prefix = "[Utils.random_file_from_dir]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Get random file / name from path [{path}]")

        # Actually get the random file from the directory
        r = random.choice([f"{path}{os.path.sep}{name}" for name in os.listdir(path)])

        # Debug and return the path
        if not silent:
            logging.info(f"{depth}{debug_prefix} Got file [{r}], ")

        return r

    # Get the basename of a path
    def get_basename(self, path, depth = LOG_NO_DEPTH, silent = False):
        debug_prefix = "[Utils.get_basename]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Get basename of path [{path}]")

        # Actually get the basename
        basename = os.path.basename(path)

        # Debug and return the basename
        if not silent:
            logging.info(f"{depth}{debug_prefix} Basename is [{basename}]")

        return basename
    
    # Return an absolute path always, pointing to the 
    def get_abspath(self, path, depth = LOG_NO_DEPTH, silent = False):
        debug_prefix = "[Utils.get_abspath]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Get abspath of path [{path}]")

        # On Linux / MacOS we expand the ~ to the current user's home directory, ~ = /home/$USER
        if self.os in ["linux", "macos"]:
            if not silent:
                logging.debug(f"{depth}{debug_prefix} POSIX: Expanding path with user home folder ~ if any")

            # Expand the path
            path = os.path.expanduser(path)

            if not silent:
                logging.debug(f"{depth}{debug_prefix} POSIX: Expanded path is [{path}]")

        # Actually get the absolute path, that is, if we're on the file /home/user/folder and type
        # ./binary we are actually referring it as /home/user/folder/binary, that is the absolute
        # path, not the relative to where we are at, this is optimal because the user can be on a 
        # shell with a different working directory executing our Python scripts
        abspath = os.path.abspath(path)

        # Did the path changed at all?
        if (abspath != path) and (not silent):
            logging.debug(f"{depth}{debug_prefix} Original path changed!! It probably was a relative reference [{path}] -> [{abspath}]")

        # Get the real path
        abs_realpath = self.get_realpath(path = abspath, depth = ndepth, silent = False)

        if not silent:
            logging.info(f"{depth}{debug_prefix} Return absolute and real path: [{abs_realpath}]")

        return abs_realpath
    
    # Some files can be symlinks on *nix or shortcuts on Windows, get the true real path
    def get_realpath(self, path, depth = LOG_NO_DEPTH, silent = False):
        debug_prefix = "[Utils.get_realpath]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Get realpath of path [{path}]")

        # Actually get the realpath
        realpath = os.path.realpath(path)

        # Did the path changed at all?
        if (not realpath == path) and (not silent):
            logging.debug(f"{depth}{debug_prefix} Got and returning realpath of [{path}] -> [{realpath}")
            
        return realpath

    # Get the filename without extension /home/linux/file.ogg -> "file"
    def get_filename_no_extension(self, path, depth = LOG_NO_DEPTH, silent = False):
        debug_prefix = "[Utils.get_filename_no_extension]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Get filename without extension of path [{path}]")

        # Actually get the filename without extension
        filename_no_ext = os.path.splitext(os.path.basename(self.get_abspath(path)))[0]

        # Log what we'll return
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Got and returning filename [{filename_no_ext}]")

        return filename_no_ext
    
    # Get the parent directory of a given path
    def get_path_parent_dir(self, path, depth = LOG_NO_DEPTH, silent = False):
        debug_prefix = "[Utils.get_path_parent_dir]"
        ndepth = depth + LOG_NEXT_DEPTH
    
        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Get the parent directory of the path [{path}]")
        
        # Get the dirname of the path
        parent = os.path.dirname(self.get_abspath(path))

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Parent directory is [{parent}]")
        
        return parent

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
    def load_yaml(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.load_yaml]"
        ndepth = depth + LOG_NEXT_DEPTH
        
        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Loading YAML file from path [{path}], getting absolute realpath first")

        # Get absolute and realpath
        path = self.get_abspath(path, depth = ndepth, silent = True)

        # Error assertion
        self.assert_file(path)

        # Open file in read mode
        with open(path, "r") as f:
            data = yaml.load(f, Loader = yaml.FullLoader)

        # Log read data
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Loaded data is: {data}")

        # Return the data
        return data
    
    # Save a dictionary to a YAML file, make sure the directory exists first..
    def dump_yaml(self, data, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.dump_yaml]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Dumping some data to YAML located at: [{path}], getting absolute realpath first")
            logging.debug(f"{depth}{debug_prefix} Data being dumped: [{data}]")

        # Make sure the parent path exists
        self.mkparent_dne(path)

        # Get absolute and realpath
        path = self.get_abspath(path, depth = ndepth, silent = True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style = False)

    # Load a toml and return its content
    def load_toml(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.load_toml]"
        ndepth = depth + LOG_NEXT_DEPTH
        
        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Loading TOML file from path [{path}], getting absolute realpath first")

        # Get absolute and realpath
        path = self.get_abspath(path, depth = ndepth, silent = True)

        # Error assertion
        self.assert_file(path)

        # Open file in read mode
        with open(path, "r") as f:
            data= toml.loads(f.read())

        # Log read data
        if not silent:
            logging.debug(f"{depth}{debug_prefix} Loaded data is: {data}")

        # Return the data
        return data
    
    # Save a dictionary to a TOML file, make sure the directory exists first..
    def dump_toml(self, data, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.dump_toml]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Dumping some data to TOML located at: [{path}], getting absolute realpath first")
            logging.debug(f"{depth}{debug_prefix} Data being dumped: [{data}]")

        # Make sure the parent path exists
        self.mkparent_dne(path)

        # Get absolute and realpath
        path = self.get_abspath(path, depth = ndepth, silent = True)

        with open(path, "w") as f:
            f.write(toml.dumps(data))

    # Waits until file exist
    def until_exist(self, path, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.until_exist]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.warn(f"{depth}{debug_prefix} Waiting for file or diretory: [{path}]")

        while True:
            time.sleep(0.1)
            if os.path.exists(path):
                break
        
    # $ mv A B
    def move(self, src, dst, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.move]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Moving path [{src}] -> [{dst}]")

        # Make sure we have the absolute and real path of the targets
        src = self.get_abspath(src, depth = ndepth, silent = silent)
        dst = self.get_abspath(dst, depth = ndepth, silent = silent)

        # Only move if the target directory doesn't exist
        if not os.path.exists(dst):
            shutil.move(src, dst)
        else:
            err = f"{depth}{debug_prefix} Target path already exist"
            logging.error(err)
            raise RuntimeError(err)
    
    # $ cp A B
    def copy(self, src, dst, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.copy]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Copying path [{src}] -> [{dst}]")

        # Make sure we have the absolute and real path of the targets
        src = self.get_abspath(src, depth = ndepth, silent = silent)
        dst = self.get_abspath(dst, depth = ndepth, silent = silent)

        # Copy the directories
        # Only move if the target directory doesn't exist
        if not os.path.exists(dst):
            shutil.copy(src, dst)
        else:
            err = f"{depth}{debug_prefix} Target path already exist"
            logging.error(err)
            raise RuntimeError(err)

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
    def has_executable_with_name(self, binary, depth = LOG_NO_DEPTH, silent = False) -> None:
        debug_prefix = "[Utils.has_executable_with_name]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Checking we can find the executable [{binary}] in PATH")

        # Tell if we can find the binary
        exists = shutil.which(binary) is not None

        # If it doesn't exist show warning, no need to quit
        if not silent:
            msg = f"{depth}{debug_prefix} Executable exists: [{exists}]"

            # Info if exists else warn
            if exists:
                logging.info(msg)
            else:
                logging.warn(msg)

        return exists
    
    # Get a executable from path, returns False if it doesn't exist
    def get_executable_with_name(self, binary, extra_paths = [], depth = LOG_NO_DEPTH, silent = False):
        debug_prefix = "[Utils.get_executable_with_name]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if not silent:
            logging.info(f"{depth}{debug_prefix} Get executable with name [{binary}]")

        # Force list variable
        extra_paths = self.force_list(extra_paths)
        search_path = os.environ["PATH"] + os.pathsep + os.pathsep.join(extra_paths)

        # Log search paths
        if not silent:
            logging.warn(f"{depth}{debug_prefix} Extra paths to search: [{extra_paths}]")
            logging.warn(f"{depth}{debug_prefix} Full search path: [{search_path}]")

        # Locate it
        locate = shutil.which(binary, path = search_path)

        # If it's not found then return False
        if locate is None:
            if not silent:
                logging.warn(f"{depth}{debug_prefix} Couldn't find binary, returning False..")
            return False
            
        # Else return its path
        if not silent:
            logging.info(f"{depth}{debug_prefix} Binary found and located at [{locate}]")

        return locate
    
    # If data is string, "abc" -> ["abc"], if data is list, return data
    def force_list(self, data):
        if not isinstance(data, list):
            data = [data]
        return data

    # Get one (astronomically guaranteed) unique id, upper(uuid4)
    # purpose key is for logging messages so we identify which identifier is binded to what object
    def get_unique_id(self, purpose = "", depth = LOG_NO_DEPTH, silent = False) -> str:
        debug_prefix = "[Utils.get_unique_id]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Get an uppercase uuid4
        unique_id = str(uuid.uuid4()).upper()[0:8]

        # Change the message based on if we have or have not a purpose
        if not silent:
            if purpose:
                message = f"{depth}{debug_prefix} Get unique identifier for [{purpose}]: [{unique_id}]"
            else:
                message = f"{depth}{debug_prefix} Get unique identifier: [{unique_id}]"

            # Log the message
            logging.info(message)

        return unique_id


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
    
# Python's subprocess utilities because I'm lazy remembering things
class SubprocessUtils():

    def __init__(self, name, utils, context):

        debug_prefix = "[SubprocessUtils.__init__]"

        self.name = name
        self.utils = utils
        self.context = context

        print(debug_prefix, "Creating SubprocessUtils with name: [%s]" % name)

    # Get the commands from a list to call the subprocess
    def from_list(self, list):

        debug_prefix = "[SubprocessUtils.run]"

        print(debug_prefix, "Getting command from list:")
        print(debug_prefix, list)

        self.command = list

    # Run the subprocess with or without a env / working directory
    def run(self, working_directory=None, env=None, shell=False):

        debug_prefix = "[SubprocessUtils.run]"
        
        print(debug_prefix, "Popen SubprocessUtils with name [%s]" % self.name)
        
        # Copy the environment if nothing was changed and passed as argument
        if env is None:
            env = os.environ.copy()
        
        # Runs the subprocess based on if we set or not a working_directory
        if working_directory == None:
            self.process = subprocess.Popen(self.command, env=env, stdout=subprocess.PIPE, shell=shell)
        else:
            self.process = subprocess.Popen(self.command, env=env, cwd=working_directory, stdout=subprocess.PIPE, shell=shell)

    # Get the newlines from the subprocess
    # This is used for communicating Dandere2x C++ with Python, simplifies having dealing with files
    def realtime_output(self):
        while True:
            # Read next line
            output = self.process.stdout.readline()

            # If output is empty and process is not alive, quit
            if output == '' and self.process.poll() is not None:
                break
            
            # Else yield the decoded output as subprocess send bytes
            if output:
                yield output.strip().decode("utf-8")

    # Wait until the subprocess has finished
    def wait(self):

        debug_prefix = "[SubprocessUtils.wait]"

        print(debug_prefix, "Waiting SubprocessUtils with name [%s] to finish" % self.name)

        self.process.wait()

    # Kill subprocess
    def terminate(self):

        debug_prefix = "[SubprocessUtils.terminate]"

        print(debug_prefix, "Terminating SubprocessUtils with name [%s]" % self.name)

        self.process.terminate()

    # See if subprocess is still running
    def is_alive(self):

        debug_prefix = "[SubprocessUtils.is_alive]"

        # Get the status of the subprocess
        status = self.process.poll()

        # None? alive
        if status == None:
            return True
        else:
            print(debug_prefix, "SubprocessUtils with name [%s] is not alive" % self.name)
            return False