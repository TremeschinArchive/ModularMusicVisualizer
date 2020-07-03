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

import shutil
import math
import yaml
import sys
import os


class Miscellaneous():

    def __init__(self):
        self.version = "1.0.0rc1"
        self.greeter_message()

    def greeter_message(self):

        terminal_width = shutil.get_terminal_size()[0]

        bias = " "*(math.floor(terminal_width/2) - 14)

        message = f"""
{"-"*terminal_width}
{bias} __  __   __  __  __     __
{bias}|  \/  | |  \/  | \ \   / /
{bias}| |\/| | | |\/| |  \ \ / / 
{bias}| |  | | | |  | |   \ V /  
{bias}|_|  |_| |_|  |_|    \_/   
{bias}
{bias}  Modular Music Visualizer                        
{bias}{(21-len("Version")-len(self.version))*" "}Version {self.version}
{"-"*terminal_width}
        """

        print(message)


class Utils():

    def __init__(self):
        self.ROOT = self.get_root()

    # Make directory if it does not exist
    def mkdir_dne(self, path):
        if isinstance(path, list):
            for p in path:
                os.makedirs(p, exist_ok=True)
        else:
            os.makedirs(path, exist_ok=True)

    # Get the directory this file is in if run from source or from a release
    def get_root(self):
        if getattr(sys, 'frozen', False):    
            return os.path.dirname(os.path.abspath(sys.executable))
        else:
            return os.path.dirname(os.path.abspath(__file__))

    def get_basename(self, path):
        return os.path.basename(path)

    def get_filename_no_extension(self, path):
        (f, ext) = os.path.splitext(path)
        return f
    
    # Load a yaml and return its content
    def load_yaml(self, path):
        with open(path, "r") as f:
            return yaml.load(f, Loader=yaml.FullLoader)
