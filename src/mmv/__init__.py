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
from mmv.common.cmn_download import Download
from mmv.common.cmn_utils import Utils
import subprocess
import tempfile
import logging
import struct
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
{bias} Modular Music Visualizer                      
{bias[:-1]}{(21-len("Version")-len(self.version))*" "}Version {self.version}
{"-"*self.terminal_width}
"""
        logging.info(message)

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

    # Main interface class, mainly sets up root dirs, get config, distributes classes
    def __init__(self, depth = PACKAGE_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVInterface.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Versioning, greeter message
        self.terminal_width = shutil.get_terminal_size()[0]
        self.version = "2.5-unite"

        # Can only run on Python 64 bits, this expression returns 32 if 32 bit installation
        # and 64 if 64 bit installation, we assert that (assume it's true, quit if it isn't)
        assert (struct.calcsize("P") * 8) == 64, (
            "You don't have an 64 bit Python installation, MMV will not work on 32 bit Python "
            "because skia-python package only distributes 64 bit Python wheels (bundles).\n"
            "This is out of my control, Skia devs don't release 32 bit version of Skia anyways\n\n"
            "See issue [https://github.com/kyamagu/skia-python/issues/21]"
        )

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
        logging.info(f"{depth}{debug_prefix} (os.path.sep) is [{sep}]")

        # # Create interface's classes

        logging.info(f"{depth}{debug_prefix} Creating Utils() class")
        self.utils = Utils()

        logging.info(f"{depth}{debug_prefix} Creating Download() class")
        self.download = Download()

        # # Common directories between packages

        # Externals
        self.externals_dir = f"{self.MMV_INTERFACE_ROOT}{sep}externals"
        logging.info(f"{depth}{debug_prefix} Externals dir is [{self.externals_dir}]")
        self.utils.mkdir_dne(path = self.externals_dir, depth = ndepth)

        # Downloads (inside externals)
        self.downloads_dir = f"{self.MMV_INTERFACE_ROOT}{sep}externals{sep}downloads"
        logging.info(f"{depth}{debug_prefix} Downloads dir is [{self.downloads_dir}]")
        self.utils.mkdir_dne(path = self.downloads_dir, depth = ndepth)

        # Data dir
        self.data_dir = f"{self.MMV_INTERFACE_ROOT}{sep}data"
        logging.info(f"{depth}{debug_prefix} Data dir is [{self.data_dir}]")
        self.utils.mkdir_dne(path = self.data_dir, depth = ndepth)

        # # Common files

        self.last_session_info_file = f"{self.data_dir}{sep}last_session_info.toml"
        logging.info(f"{depth}{debug_prefix} Last session info file is [{self.last_session_info_file}], resetting it..")
        self.utils.reset_file(self.last_session_info_file)

        # Code flow management
        if self.prelude["flow"]["stop_at_initialization"]:
            logging.critical(f"{depth}{debug_prefix} Exiting as stop_at_initialization key on prelude.toml is True")
            sys.exit(0)


    # # [ QOL // Micro management ] # #


    # Make sure we have FFmpeg
    def download_check_ffmpeg(self, making_release = False, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVInterface.download_check_ffmpeg]"
        ndepth = depth + LOG_NEXT_DEPTH
        logging.info(LOG_SEPARATOR)

        # Log action
        logging.info(f"{depth}{debug_prefix} Checking for FFmpeg on Linux or downloading for Windows / if (making release: [{making_release}]")

        if getattr(sys, 'frozen', False):
            logging.info(f"{depth}{debug_prefix} Not checking ffmpeg.exe because is executable build.. should have ffmpeg.exe bundled?")
            return

        sep = os.path.sep

        # If the code is being run on a Windows OS
        if (self.os == "windows") or (making_release):

            # Temporary directory if needed
            # self.temp_dir = tempfile.gettempdir()
            # logging.info(f"{depth}{debug_prefix} Temp dir is: [{self.temp_dir}]")

            if making_release:
                logging.info(f"{depth}{debug_prefix} Getting FFmpeg for Windows because making_release=True")

            # Where we should find the ffmpeg binary
            FINAL_FFMPEG_FINAL_BINARY = self.externals_dir + f"{sep}ffmpeg.exe"

            # If we don't have FFmpeg binary on externals dir
            if not os.path.isfile(FINAL_FFMPEG_FINAL_BINARY):

                # Get the latest release number of ffmpeg
                ffmpeg_release = self.download.get_html_content("https://www.gyan.dev/ffmpeg/builds/release-version")
                logging.info(f"{depth}{debug_prefix} FFmpeg release number is [{ffmpeg_release}]")

                # Where we'll save the compressed zip of FFmpeg
                ffmpeg_7z = self.downloads_dir + f"{sep}ffmpeg-{ffmpeg_release}-essentials_build.7z"

                # Download FFmpeg build
                self.download.wget(
                    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z",
                    ffmpeg_7z, f"FFmpeg v={ffmpeg_release}"
                )

                # Extract the files
                self.download.extract_file(ffmpeg_7z, self.downloads_dir)

                # Where the FFmpeg binary is located
                ffmpeg_bin = ffmpeg_7z.replace(".7z", "") + f"{sep}bin{sep}ffmpeg.exe"

                # Move to this directory
                self.utils.move(ffmpeg_bin, FINAL_FFMPEG_FINAL_BINARY)

            else:
                logging.info(f"{depth}{debug_prefix} Already have [ffmpeg.exe] downloaded and extracted at [{FINAL_FFMPEG_FINAL_BINARY}]")
        else:
            # We're on Linux so checking ffmpeg external dependency
            logging.info(f"{depth}{debug_prefix} You are using Linux, please make sure you have FFmpeg package installed on your distro, we'll just check for it now..")
            self.utils.has_executable_with_name("ffmpeg", depth = ndepth)
        logging.info(STEP_SEPARATOR)


    # Make sure we have MPV
    def download_check_mpv(self, making_release = False, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVInterface.download_check_mpv]"
        ndepth = depth + LOG_NEXT_DEPTH
        logging.info(LOG_SEPARATOR)

        # Log action
        logging.info(f"{depth}{debug_prefix} Checking for MPV on Linux or downloading for Windows / if (making release: [{making_release}]")

        if getattr(sys, 'frozen', False):
            logging.info(f"{depth}{debug_prefix} Not checking mpv.exe because is executable build.. should have ffmpeg.exe bundled?")
            return

        sep = os.path.sep

        # If the code is being run on a Windows OS
        if (self.os == "windows") or (making_release):

            if making_release:
                logging.info(f"{depth}{debug_prefix} Getting mpv for Windows because making_release=True")

            # Where we should find the ffmpeg binary
            FINAL_MPV_FINAL_BINARY = self.externals_dir + f"{sep}mpv{sep}mpv.exe"

            # If we don't have FFmpeg binary on externals dir
            if not os.path.isfile(FINAL_MPV_FINAL_BINARY):

                # Where we'll save the compressed zip of FFmpeg
                mpv_7z = self.downloads_dir + f"{sep}mpv-x86_64-20201220-git-dde0189.7z"

                # Download FFmpeg build
                self.download.wget(
                    "https://sourceforge.net/projects/mpv-player-windows/files/64bit/mpv-x86_64-20201220-git-dde0189.7z/download",
                    mpv_7z, f"MPV v=20201220-git-dde0189"
                )

                # Where to extract final mpv
                mpv_extracted_folder = f"{self.externals_dir}{sep}mpv"
                self.utils.mkdir_dne(path = mpv_extracted_folder, depth = ndepth)

                # Extract the files
                self.download.extract_file(mpv_7z, mpv_extracted_folder)

            else:
                logging.info(f"{depth}{debug_prefix} Already have [mpv.exe] downloaded and extracted at [{FINAL_MPV_FINAL_BINARY}]")
        else:
            # We're on Linux so checking ffmpeg external dependency
            logging.info(f"{depth}{debug_prefix} You are using Linux, please make sure you have MPV package installed on your distro, we'll just check for it now..")
            self.utils.has_executable_with_name("mpv", depth = ndepth)
        logging.info(STEP_SEPARATOR)


    # Make sure we have musescore
    def download_check_musescore(self, making_release = False, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVInterface.download_check_mpv]"
        ndepth = depth + LOG_NEXT_DEPTH
        logging.info(LOG_SEPARATOR)

        # Log action
        logging.info(f"{depth}{debug_prefix} Checking for Musescore on Linux or downloading for Windows / if (making release: [{making_release}]")

        if getattr(sys, 'frozen', False):
            logging.info(f"{depth}{debug_prefix} Not checking musescore.exe because is executable build.. should have ffmpeg.exe bundled?")
            return

        sep = os.path.sep

        # If the code is being run on a Windows OS
        if (self.os == "windows") or (making_release):

            if making_release:
                logging.info(f"{depth}{debug_prefix} Getting mpv for Windows because making_release=True")

            # Where we should find the ffmpeg binary
            FINAL_MUSESCORE_FINAL_BINARY = self.externals_dir + f"{sep}musescore.exe"

            # If we don't have FFmpeg binary on externals dir
            if not os.path.isfile(FINAL_MUSESCORE_FINAL_BINARY):
                
                musescore_version = "v3.5.2/MuseScorePortable-3.5.2.311459983-x86.paf.exe"

                # Download FFmpeg build
                self.download.wget(
                    f"https://cdn.jsdelivr.net/musescore/{musescore_version}",
                    FINAL_MUSESCORE_FINAL_BINARY, f"Musescore v=[{musescore_version}]"
                )

            else:
                logging.info(f"{depth}{debug_prefix} Already have [musescore.exe] downloaded and extracted at [{FINAL_MUSESCORE_FINAL_BINARY}]")
        else:
            # We're on Linux so checking ffmpeg external dependency
            logging.info(f"{depth}{debug_prefix} You are using Linux, please make sure you have musescore package installed on your distro, we'll just check for it now.. or go to [https://musescore.org/en/download] and install for your platform")
            if not self.utils.has_executable_with_name("musescore", depth = ndepth):
                sys.exit(-1)
        logging.info(STEP_SEPARATOR)
