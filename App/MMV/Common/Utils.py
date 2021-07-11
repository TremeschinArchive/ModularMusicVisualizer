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

import glob
import hashlib
import logging
import math
import os
import random
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import MMV.Common.AnyLogger
import toml
import yaml


class Utils:
    # Get the desired name from a dict matching against os.name
    @staticmethod
    def GetOS():
        return {
            "posix": "Linux",
            "nt": "Windows",
            "darwin": "MacOS"
        }.get(os.name)

    @staticmethod
    def AllSubdirectories(path):
        return [item for item in Path(path).rglob("*") if item.is_dir]

    @staticmethod
    def AssignLocals(data):
        for key, value in data.items():
            if key != "self": data["self"].__dict__[key] = value

    @staticmethod
    def FindBinary(binary, platform="Linux"):
        if (platform == "Windows") and (not binary.endswith(".exe")):
            binary += ".exe"
        PATH = os.environ.get("PATH") + ":".join(sys.path)
        return shutil.which(binary, path=PATH)

    @staticmethod
    def ForceList(data):
        if not isinstance(data, list):
            data = [data]
        return data

    @staticmethod
    def ResolvePath(path):
        return Path(path).expanduser().resolve()

    @staticmethod
    def LoadYaml(path):
        return yaml.load(Utils.ResolvePath(path).read_text(), Loader=yaml.FullLoader)

    # # "Old" / to rewrite

    def __init__(self):
        self.os = self.get_os()

    # Convert to pathlib.Path
    def enforce_pathlib_Path(self, path):
        if isinstance(path, str): path = Path(path)
        return path

    def reset_dir(self, path: Path):
        dpfx = "[Utils.reset_dir]"
        logging.info(f"{dpfx} Reset directory (remove")
        assert path.is_dir, f"{dpfx} Path [{path}] must be directory"
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
        dpfx = "[Utils.random_file_from_dir]"

        # Log action
        if not silent:
            logging.debug(f"{dpfx} Get random file / name from path [{path}]")

        # Actually get the random file from the directory
        r = random.choice([f"{path}{os.path.sep}{name}" for name in os.listdir(path)])

        # Debug and return the path
        if not silent:
            logging.info(f"{dpfx} Got file [{r}], ")

        return r
    
    

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

    
    # Save a dictionary to a YAML file, make sure the directory exists first..
    def dump_yaml(self, data, path, silent = False) -> None:
        dpfx = "[Utils.dump_yaml]"

        # Log action
        if not silent:
            logging.info(f"{dpfx} Dumping some data to YAML located at: [{path}], getting absolute realpath first")
            logging.debug(f"{dpfx} Data being dumped: [{data}]")

        # Get absolute and realpath
        path = self.get_absolute_realpath(path, silent = True)

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style = False)

    # Load a toml and return its content
    def load_toml(self, path, silent = False) -> None:
        dpfx = "[Utils.load_toml]"

        # Log action
        if not silent:
            logging.info(f"{dpfx} Loading TOML file from path [{path}], getting absolute realpath first")

        # Error assertion
        self.assert_file(path)

        # Open file in read mode
        with open(path, "r") as f:
            data= toml.loads(f.read())

        # Log read data
        if not silent:
            logging.debug(f"{dpfx} Loaded data is: {data}")

        # Return the data
        return data
    
    # Save a dictionary to a TOML file, make sure the directory exists first..
    def dump_toml(self, data, path, silent = False) -> None:
        dpfx = "[Utils.dump_toml]"

        # Log action
        if not silent:
            logging.info(f"{dpfx} Dumping some data to TOML located at: [{path}], getting absolute realpath first")
            logging.debug(f"{dpfx} Data being dumped: [{data}]")

        # Make sure the parent path exists
        self.mkparent_dne(path)

        # Get absolute and realpath
        path = self.get_absolute_realpath(path, silent = True)

        with open(path, "w") as f:
            f.write(toml.dumps(data))

    # Waits until file exist
    def until_exist(self, path, silent = False) -> None:
        dpfx = "[Utils.until_exist]"

        # Log action
        if not silent:
            logging.warning(f"{dpfx} Waiting for file or diretory: [{path}]")

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
        dpfx = "[Utils.has_executable_with_name]"

        # Log action
        if not silent:
            logging.info(f"{dpfx} Checking we can find the executable [{binary}] in PATH")

        # Tell if we can find the binary
        exists = shutil.which(binary) is not None

        # If it doesn't exist show warning, no need to quit
        if not silent:
            msg = f"{dpfx} Executable exists: [{exists}]"

            # Info if exists else warn
            if exists:
                logging.info(msg)
            else:
                logging.warning(msg)

        return exists
    
    # Get a executable from path, returns False if it doesn't exist
    def get_executable_with_name(self, binary, extra_paths = [], silent = False):
        dpfx = "[Utils.get_executable_with_name]"

        # Log action
        if not silent:
            logging.info(f"{dpfx} Get executable with name [{binary}]")

        # Force list variable
        extra_paths = self.force_list(extra_paths)
        search_path = os.environ["PATH"] + os.pathsep + os.pathsep.join([str(path) for path in extra_paths])

        # Log search paths
        if not silent:
            logging.debug(f"{dpfx} Extra paths to search: [{extra_paths}]")
            logging.debug(f"{dpfx} Full search path: [{search_path}]")

        # Locate it
        locate = shutil.which(binary, path = search_path)

        # If it's not found then return False
        if locate is None:
            if not silent:
                logging.warning(f"{dpfx} Couldn't find binary, returning False..")
            return False
            
        # Else return its path
        if not silent:
            logging.info(f"{dpfx} Binary found and located at [{locate}]")

        return locate
    
    # If data is string, "abc" -> ["abc"], if data is list, return data
    def force_list(self, data):
        if not isinstance(data, list):
            data = [data]
        return data

    # Get one (astronomically guaranteed) unique id, upper(uuid4)
    # purpose key is for logging messages so we identify which identifier is binded to what object
    def get_unique_id(self, purpose = "", silent = False) -> str:
        dpfx = "[Utils.get_unique_id]"

        # Get an uppercase uuid4
        unique_id = str(uuid.uuid4()).upper()[0:8]

        # Change the message based on if we have or have not a purpose
        if not silent:
            if purpose:
                message = f"{dpfx} Get unique identifier for [{purpose}]: [{unique_id}]"
            else:
                message = f"{dpfx} Get unique identifier: [{unique_id}]"

            # Log the message
            logging.info(message)

        return unique_id

    # "true" if True else "false"
    def bool_to_string(self, value): return "true" if value else "false"
