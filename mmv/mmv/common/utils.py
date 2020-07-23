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


class Utils():

    def __init__(self):
        self.ROOT = self.get_root()

    # Make directory if it does not exist
    def mkdir_dne(self, path):
        path = self.get_abspath(path)
        if isinstance(path, list):
            for p in path:
                os.makedirs(p, exist_ok=True)
        else:
            os.makedirs(path, exist_ok=True)
    
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
            print(debug_prefix, "Directory exists, skipping... [%s]" % path)

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
        if getattr(sys, 'frozen', False):    
            return os.path.dirname(os.path.abspath(sys.executable))
        else:
            return os.path.dirname(os.path.abspath(__file__))

    # Get the basename of a path
    def get_basename(self, path):
        return os.path.basename(path)
    
    # Return an absolute path always
    def get_abspath(self, path):
        
        debug_prefix = "[Utils.get_abspath]"
       
        abspath = os.path.abspath(path)
        print(debug_prefix, "abspath of [%s] > [%s]" % (path, abspath))
        return abspath

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
    def get_hash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    # Load a yaml and return its content
    def load_yaml(self, path):
        with open(path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    # Waits until file exist or controller stop var is True
    def until_exist(self, path):

        debug_prefix = "[Utils.until_exist]"

        print(debug_prefix, "Waiting for file or diretory: [%s]" % path)

        while True:
            time.sleep(0.1)
            if os.path.exists(path):
                break
        
    # $ mv A B
    def move(self, src, dst, shell=False):
        command = ["mv", src, dst]
        print(' '.join(command))
        subprocess.run(command, stdout=subprocess.PIPE, shell=shell)
    
    # $ cp A B
    def copy(self, src, dst, shell=False):
        command = ["cp", src, dst]
        print(' '.join(command))
        subprocess.run(command, stdout=subprocess.PIPE, shell=shell)

    # Check if either type A = wanted[0] and B = wanted[1] or the opposite
    def is_matching_type(self, items, wanted):
        # print("Checking items", items, "on wanted", wanted)
        for index, item in enumerate(items):
            for wanted_index, wanted_type in enumerate(wanted):
                if isinstance(item, wanted_type):
                    del wanted[wanted_index]
                    continue
                else:
                    return False
        return True


class DataUtils():
    
    def dictionary_items_in_between(self, data, start, end):
        return {k: v for k, v in data.items() if k > start and k < end}
    
    def equal_slices(self, array, n):
        size = len(array)
        return [ array[i: min(i+n, size) ] for i in range(0, size, n) ]
    
    def equal_bars_average(self, data, nbars, mode):
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