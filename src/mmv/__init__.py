"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Interface class for all MMV goodness

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, PACKAGE_DEPTH, LOG_NO_DEPTH, LOG_SEPARATOR, STEP_SEPARATOR
import logging
import shutil
import toml
import math
import sys
import os


# Class that distributes MMV packages, sets up logging and behavior
# This class is distributed as being called "interface" among mmvskia
# and mmvshader packages, which this one have the "prelude" attribute
# which is the dictionary of the file prelude.toml containing
# general behavior of MMV
class MMVInterface:

    # Hello world!
    def greeter_message(self, depth = PACKAGE_DEPTH) -> None:
        debug_prefix = "[MMVInterface.greeter_message]"
        ndepth = depth + LOG_NEXT_DEPTH

        self.terminal_width = shutil.get_terminal_size()[0]

        bias = " "*(math.floor(self.terminal_width/2) - 14)

        message = \
f"""{depth}{debug_prefix} Show greeter message\n{"-"*self.terminal_width}
{bias} __  __   __  __  __     __
{bias}|  \\/  | |  \\/  | \\ \\   / /
{bias}| |\\/| | | |\\/| |  \\ \\ / / 
{bias}| |  | | | |  | |   \\ V /  
{bias}|_|  |_| |_|  |_|    \\_/   
{bias}
{bias[:-8]}  Modular Music Visualizer Skia Edition                       
{bias[:-1]}{(21-len("Version")-len(self.version))*" "}Version {self.version}
{"-"*self.terminal_width}
"""
        logging.info(message)

    # Start default configs, creates wrapper classes
    def __init__(self, depth = PACKAGE_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVInterface.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Versioning, greeter message
        self.terminal_width = shutil.get_terminal_size()[0]
        self.version = "2.4-dev-not-working"

        # # Get this file's path

        sep = os.path.sep

        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_main.MMV_INTERFACE_ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.MMV_INTERFACE_ROOT = os.path.dirname(os.path.abspath(__file__))
            print(f"{depth}{debug_prefix} Running directly from source code")
            print(f"{depth}{debug_prefix} Modular Music Visualizer Python package [__init__.py] located at [{self.MMV_INTERFACE_ROOT}]")
        else:
            self.MMV_INTERFACE_ROOT = os.path.dirname(os.path.abspath(sys.executable))
            print(f"{depth}{debug_prefix} Running from release (sys.executable..?)")
            print(f"{depth}{debug_prefix} Modular Music Visualizer executable located at [{self.MMV_INTERFACE_ROOT}]")

        # # Load prelude configuration

        print(f"{depth}{debug_prefix} Loading prelude configuration file")
        
        # Build the path the prelude file should be located at
        prelude_file = f"{self.MMV_INTERFACE_ROOT}{sep}prelude.toml"

        print(f"{depth}{debug_prefix} Attempting to load prelude file located at [{prelude_file}], we cannot continue if this is wrong..")

        # Load the prelude file
        with open(prelude_file, "r") as f:
            self.prelude = toml.loads(f.read())
        
        print(f"{depth}{debug_prefix} Loaded prelude configuration file, data: [{self.prelude}]")

        # # # Logging 

        # # We can now set up logging as we have where this file is located at

        # # Reset current handlers if any
        
        print(f"{depth}{debug_prefix} Resetting Python's logging logger handlers to empty list")

        # Get logger and empty the list
        logger = logging.getLogger()
        logger.handlers = []

        # Handlers on logging to file and shell output, the first one if the user says to
        handlers = [logging.StreamHandler(sys.stdout)]

        # Loglevel is defined in the prelude.toml configuration
        LOG_LEVEL = {
            "critical": logging.CRITICAL,
            "debug": logging.DEBUG,
            "error": logging.ERROR,
            "info": logging.INFO,
            "warn": logging.WARN,
            "notset": logging.NOTSET,
        }.get(self.prelude["logging"]["log_level"])

        # If user chose to log to a file, add its handler..
        if self.prelude["logging"]["log_to_file"]:

            # Hard coded where the log file will be located
            # this is only valid for the last time we run this software
            self.LOG_FILE = f"{self.MMV_INTERFACE_ROOT}{sep}last_log.log"

            # Reset the log file
            with open(self.LOG_FILE, "w") as f:
                print(f"{depth}{debug_prefix} Reset log file located at [{self.LOG_FILE}]")
                f.write("")

            # Verbose and append the file handler
            print(f"{depth}{debug_prefix} Reset log file located at [{self.LOG_FILE}]")
            handlers.append(logging.FileHandler(filename = self.LOG_FILE, encoding = 'utf-8'))

        # .. otherwise just keep the StreamHandler to stdout

        log_format = {
            "informational": "[%(levelname)-8s] [%(filename)-32s:%(lineno)-3d] (%(relativeCreated)-6d) %(message)s",
            "pretty": "[%(levelname)-8s] (%(relativeCreated)-6d) %(message)s",
            "economic": "[%(levelname)s::%(filename)s::%(lineno)d] %(message)s",
            "onlymessage": "%(message)s"
        }.get(self.prelude["logging"]["log_format"])

        # Start the logging global class, output to file and stdout
        logging.basicConfig(
            level = LOG_LEVEL,
            format = log_format,
            handlers = handlers,
        )

        # :)
        self.greeter_message()

        # Start logging message
        bias = " " * ((self.terminal_width//2) - 13); print(f"{bias[:-1]}# # [ Start Logging ] # #\n")
        print("-" * self.terminal_width + "\n")

        # Log what we'll do next
        logging.info(f"{depth}{debug_prefix} We're done with the pre configuration of Python's behavior and loading prelude.toml configuration file")

        # Log precise Python version
        sysversion = sys.version.replace("\n", " ").replace("  ", " ")
        logging.info(f"{depth}{debug_prefix} Running on Python: [{sysversion}]")

        # # # FIXME: Python 3.9, go home you're drunk

        # Max python version, show info, assert, pretty print
        maximum_working_python_version = (3, 8)
        pversion = sys.version_info

        # Log and check
        logging.info(f"{depth}{debug_prefix} Checking if Python <= {maximum_working_python_version} for a working version.. ")

        # Huh we're on Python 2..?
        if pversion[0] == 2:
            logging.error(f"{depth}{debug_prefix} Please upgrade to at least Python 3")
            sys.exit(-1)
        
        # Python is ok
        if (pversion[0] <= maximum_working_python_version[0]) and (pversion[1] <= maximum_working_python_version[1]):
            logging.info(f"{depth}{debug_prefix} Ok, good python version")
        else:
            # Warn Python 3.9 is a bit unstable, even the developer had issues making it work
            logging.warn(f"{depth}{debug_prefix} Python 3.9 is acting a bit weird regarding some dependencies on some systems, while it should be possible to run, take it with some grain of salt and report back into the discussions troubles or workarounds you found?")

        # # The operating system we're on, one of "linux", "windows", "macos"

        # Get the desired name from a dict matching against os.name
        self.os = {
            "posix": "linux",
            "nt": "windows",
            "darwin": "macos"
        }.get(os.name)

        # Log which OS we're running
        logging.info(f"{depth}{debug_prefix} Running Modular Music Visualizer on Operating System: [{self.os}]")
        logging.info(f"{depth}{debug_prefix} (os.path.sep) is [{os.path.sep}]")

    # MMVSkia works with glfw plus Skia to draw on a GL canvas and pipe
    # through FFmpeg to render a final video. Have Piano Roll options
    # and modules as well!!
    def get_skia_interface(self, depth = PACKAGE_DEPTH, **kwargs):
        debug_prefix = "[MMVInterface.get_skia_interface]"
        ndepth = depth + LOG_NEXT_DEPTH
        from mmv.mmvskia import MMVSkiaInterface

        logging.info(f"{depth}{debug_prefix} Get and return MMVSkiaInterface, kwargs: {kwargs}")
        
        return MMVSkiaInterface(self, depth = ndepth, **kwargs)
    
    # MMVShader works with GLSL shaders through MPV. Currently most
    # applicable concept is post processing which bumps MMV quality
    # by a lot
    def get_shader_interface(self, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVInterface.get_shader_interface]"
        ndepth = depth + LOG_NEXT_DEPTH
        from mmv.mmvshader import MMVShaderInterface

        logging.info(f"{depth}{debug_prefix} Return MMVShaderInterface")
        
        return MMVShaderInterface(self, depth = ndepth)
