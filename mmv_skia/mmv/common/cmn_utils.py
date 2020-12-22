"""
===============================================================================

Purpose: Set of utilities to refactor other files

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

from mmv.common.cmn_constants import NEXT_DEPTH, NO_DEPTH
import subprocess
import hashlib
import random
import shutil
import glob
import math
import yaml
import time
import sys
import os


class Utils:
    def __init__(self):
        self.ROOT = self.get_root()
        self.os = self.get_os()

    # Make directory / directories if it does not exist
    def mkdir_dne(self, path):
        path = self.get_abspath(path, silent = True)
        if isinstance(path, list):
            for p in path:
                os.makedirs(p, exist_ok=True)
        else:
            os.makedirs(path, exist_ok=True)
    
    # Make file it does not exist, return True if it existed before
    def mkfile_dne(self, path):
        path = self.get_abspath(path, silent = True)
        if not os.path.isfile(path):
            with open(path, "w") as f:
                f.write("")
            return False
        return True

    # Deletes an directory, fail safe? Quits if
    def rmdir(self, path):

        debug_prefix = "[Utils.rmdir]"

        # If the asked directory is even a path
        if os.path.isdir(path):

            print(debug_prefix, "Removing dir: [%s]" % path)

            # Try removing with ignoring errors first..?
            shutil.rmtree(path, ignore_errors=True)

            # Not deleted?
            if os.path.isdir(path):
                print(debug_prefix, "Error removing directory with ignore_errors=True, trying again")

                # Remove without ignoring errors?
                shutil.rmtree(path, ignore_errors=False)

                # Still exists? oops, better quit
                if os.path.isdir(path):
                    print(debug_prefix, "COULD NOT REMOVE DIRECTORY: [%s]" % path)
                    sys.exit(-1)

            print(debug_prefix, "Removed successfully")
        else:
            print(debug_prefix, "Directory doesn't exists, skipping... [%s]" % path)

    # Copy every file of a directory to another
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
    def random_file_from_dir(self, path):
        # print("random file from path [%s]" % path)
        r = random.choice([path + os.path.sep + f for f in os.listdir(path)])
        # print("got [%s]" % r)
        return r

    # Get the directory this file is in if run from source or from a release
    def get_root(self):
        if getattr(sys, 'frozen', True):    
            return os.path.dirname(os.path.abspath(__file__))
        else:
            return os.path.dirname(os.path.abspath(sys.executable))

    # Get the basename of a path
    def get_basename(self, path):
        return os.path.basename(path)
    
    # Return an absolute path always
    def get_abspath(self, path, depth = NO_DEPTH, silent = False):
        debug_prefix = "[Utils.get_abspath]"

        if self.os == "linux":
            if not silent:
                print(debug_prefix, "Linux: Expanding path with user home folder ~ if any")
            path = os.path.expanduser(path)
       
        abspath = os.path.abspath(path)

        if not silent:
            print(debug_prefix, f"abspath of [{path}] > [{abspath}]")

        return self.get_realpath(abspath)
    
    # Some files can be symlinks on unix or shortcuts on Windows, get the true real path
    def get_realpath(self, path):
        realpath = os.path.realpath(path)

        if not realpath == path:
            print(f"[Utils.get_realpath] Realpath of [{path}] > [{realpath}")
            
        return realpath

    # Get the filename without extension /home/linux/file.ogg -> "file"
    def get_filename_no_extension(self, path):
        return os.path.splitext(os.path.basename(path))[0]
    
    # Get operating system
    def get_os(self):

        name = os.name

        # Not really specific but should work?
        if name == "posix":
            os_name = "linux"
        if name == "nt":
            os_name = "windows"

        return os_name
    
    # Get a md5 hash of a string
    def get_string_md5(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()
    
    # Calculate the md5 and sha256 of a given file path, its contents
    def get_hash_of_file(self, path):

        # Initialize blank md5 and sha256
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()

        path = self.get_realpath(path)

        # Open the file in (r)ead (b)ytes mode
        with open(path, 'rb') as f:
            while True:

                # Read 64 kB chunk data of the file
                data = f.read(1024 * 64)

                # If no more data, quit the loop
                if not data:
                    break

                # Update the md5 and sha256
                md5.update(data)
                sha256.update(data)

        # Return a named list of the hashes
        return {
            "md5": md5.hexdigest(),
            "sha256": sha256.hexdigest(),
        }

    # Load a yaml and return its content
    def load_yaml(self, path):
        path = self.get_abspath(path, silent = True)
        with open(path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    
    # Save a dictionary to a YAML file
    def save_data_to_yaml(self, data, path):
        path = self.get_abspath(path, silent = True)
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

    # Waits until file exist
    def until_exist(self, path):

        debug_prefix = "[Utils.until_exist]"

        print(debug_prefix, "Waiting for file or diretory: [%s]" % path)

        while True:
            time.sleep(0.1)
            if os.path.exists(path):
                break
        
    # $ mv A B
    def move(self, src, dst, shell=False):
        print("[Utils.move] Moving path [%s] --> [%s]" % (src, dst))
        if not os.path.exists(dst):
            shutil.move(src, dst)
        else:
            print("[Utils.move] File already exists!!")
    
    # $ cp A B
    def copy(self, src, dst, shell=False):
        print("[Utils.move] Moving path [%s] --> [%s]" % (src, dst))
        shutil.copy(src, dst)

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
    def has_executable_with_name(self, name):
        return shutil.which(name) is not None
    
    # Get a executable from path, returns False if it doesn't exist
    def get_executable_with_name(self, name, extra_paths = [None]):

        # Force list variable
        extra_paths = self.force_list(extra_paths)
        search_path = os.environ["PATH"] + os.pathsep + os.pathsep.join(extra_paths)

        # Locate it
        locate = shutil.which(name, path = search_path)

        # If it's not found then return False
        if locate is None:
            return False
            
        # Else return its path
        return locate
    
    # If data is string, "abc" -> ["abc"], if data is list, return data
    def force_list(self, data):
        if not isinstance(data, list):
            data = [data]
        return data


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
    
    # Creates nbars of "bins" from a dictionary data
    def equal_bars_average(self, data, nbars, mode):

        # Sorted keys and equal slice 'em
        sorted_data = sorted(list(data.keys()))
        slices_index = self.equal_slices(sorted_data, nbars)

        return_values = {}
        
        if mode == "average":
            for bar_index, list_indexes in enumerate(slices_index):
                total_sum = 0
                for index in list_indexes:
                    total_sum += data[index]
                average = total_sum / len(list_indexes)
                return_values[bar_index] = average

        elif mode == "max":
            for bar_index, list_indexes in enumerate(slices_index):
                values = []
                for index in list_indexes:
                    values.append(data[index])
                return_values[bar_index] = max(values)
            
        return return_values


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