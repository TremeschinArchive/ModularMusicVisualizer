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
import shutil
import yaml
import math
import time
import sys
import os


class Miscellaneous():

    def __init__(self):
        self.version = "1.1.0rc1"
        self.greeter_message()

    def greeter_message(self):

        terminal_width = shutil.get_terminal_size()[0]

        bias = " "*(math.floor(terminal_width/2) - 37)

        message = f"""
{"-"*terminal_width}
{bias} _____          _____                  _                  _              
{bias}|  __ \        / ____|                | |( )             | |             
{bias}| |__) |_   _ | |  __  _ __  __ _   __| | _   ___  _ __  | |_  ___  _ __ 
{bias}|  ___/| | | || | |_ || '__|/ _` | / _` || | / _ \| '_ \ | __|/ _ \| '__|
{bias}| |    | |_| || |__| || |  | (_| || (_| || ||  __/| | | || |_|  __/| |   
{bias}|_|     \__, | \_____||_|   \__,_| \__,_||_| \___||_| |_| \__|\___||_|   
{bias}         __/ |                                                           
{bias}        |___/                                                             
{bias}                         Cool Gradient* Images
{bias}
{bias}* and the most bizarre combinations
{bias}{(71-len("Version")-len(self.version))*" "}Version {self.version}
{"-"*terminal_width}
        """

        print(message)


class Utils():

    # Make directory if it does not exist
    def mkdir_dne(self, path):
        os.makedirs(path, exist_ok=True)



    # Get the directory this file is in if run from source or from a release
    def get_root(self):
        if getattr(sys, 'frozen', False):    
            return os.path.dirname(os.path.abspath(sys.executable))
        else:
            return os.path.dirname(os.path.abspath(__file__))
    
    # Load a yaml and return its content
    def load_yaml(self, path):
        with open(path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
    
    # Check if either type A = wanted[0] and B = wanted[1] or the opposite
    def is_matching_type(self, items, wanted):
        for item in items:
            if item in wanted:
                wanted.remove(item)
            else:
                False
        return True
    
    def until_exist(self, path):
        while True:
            if os.path.exists(path):
                break
            time.sleep(0.1)
    
    # Deletes an directory, fail safe? Quits if
    def rmdir(self, path):

        # If the asked directory is even a path
        if os.path.isdir(path):

            # Try removing with ignoring errors first..?
            shutil.rmtree(path, ignore_errors=True)

            # Not deleted?
            if os.path.isdir(path):

                # Remove without ignoring errors?
                shutil.rmtree(path, ignore_errors=False)

                # Still exists? oops, better quit
                if os.path.isdir(path):
                    sys.exit(-1)
