"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
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
import json
import logging
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import toml
from mmv.common.cmn_download import Download
from mmv.common.cmn_utils import Utils
from mmv.common.externals_manager import ExternalsManager

sys.dont_write_bytecode = True

# Class that distributes MMV packages, sets up logging and behavior;
class MMVPackageInterface:

    # Hello world!
    def greeter_message(self) -> None:
        debug_prefix = "[MMVPackageInterface.greeter_message]"

        # Get a bias for printing the message centered
        self.terminal_width = shutil.get_terminal_size()[0]
        bias = " "*(math.floor(self.terminal_width/2) - 14)

        message = \
f"""{debug_prefix} Show greeter message\n{"-"*self.terminal_width}
{bias} __  __   __  __  __     __
{bias}|  \\/  | |  \\/  | \\ \\   / /
{bias}| |\\/| | | |\\/| |  \\ \\ / / 
{bias}| |  | | | |  | |   \\ V /  
{bias}|_|  |_| |_|  |_|    \\_/   
{bias}
{bias} Modular Music Visualizer                      
{(2 + int( (self.terminal_width/2) - (len("Version") + len(self.version)/2) ))*" "}Version {self.version}
{"-"*self.terminal_width}
"""
        logging.info(message)

    # Thanks message with some official links, warnings
    def thanks_message(self):
        debug_prefix = "[MMVPackageInterface.thanks_message]"

        # Get a bias for printing the message centered
        self.terminal_width = shutil.get_terminal_size()[0]
        bias = " "*(math.floor(self.terminal_width/2) - 45)

        message = \
f"""{debug_prefix} Show thanks message
\n{"-"*self.terminal_width}\n
{bias}[+-------------------------------------------------------------------------------------------+]
{bias} |                                                                                           |
{bias} |              :: Thanks for using the Modular Music Visualizer project !! ::               |
{bias} |              ==============================================================               |
{bias} |                                                                                           |
{bias} |  Here's a few official links for MMV:                                                     |
{bias} |                                                                                           |
{bias} |    - Telegram group:          [          https://t.me/modular_music_visualizer         ]  |
{bias} |    - GitHub Repository:       [ https://github.com/Tremeschin/modular-music-visualizer ]  |
{bias} |    - GitLab Repository:       [ https://gitlab.com/Tremeschin/modular-music-visualizer ]  |
{bias} |                                                                                           |
{bias} |  > Always check for the copyright info on the material you are using (audios, images)     |
{bias} |  before distributing the content generated with MMV, I take absolutely no responsibility  |
{bias} |  for any UGC (user generated content) violations. See LICENSE file as well.               |
{bias} |                                                                                           |
{bias} |  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  |
{bias} |                                                                                           |
{bias} |             Don't forget sharing your releases made with MMV on the discussion groups :)  |
{bias} |                 Feel free asking for help or giving new ideas for the project as well !!  |
{bias} |                                                                                           |
{bias}[+-------------------------------------------------------------------------------------------+]
\n{"-"*self.terminal_width}
"""
        logging.info(message)

    # MMVShader for some post processing or visualization generation
    def ___printshadersmode(self):
        if not hasattr(self, "___printshader"):
            self.___printshader = None
            self.terminal_width = shutil.get_terminal_size()[0]
            bias = " "*(math.floor(self.terminal_width/2) - 19)
            message = \
f"""Show extension\n{"="*self.terminal_width}
{bias} _____ _               _               
{bias}/  ___| |             | |              
{bias}\\ `--.| |__   __ _  __| | ___ _ __ ___ 
{bias} `--. \\ '_ \\ / _` |/ _` |/ _ \\ '__/ __|
{bias}/\\__/ / | | | (_| | (_| |  __/ |  \\__ \\
{bias}\\____/|_| |_|\\__,_|\\__,_|\\___|_|  |___/
{bias}                            
{bias}
{bias}             + MMV Mode +
{"="*self.terminal_width}
"""
            logging.info(message)

    def get_sombrero(self, **kwargs):
        self.___printshadersmode()
        from mmv.sombrero.sombrero_main import SombreroMGL
        return SombreroMGL

    # Return one (usually required) setting up encoder unless using preview window
    def get_ffmpeg_wrapper(self):
        debug_prefix = "[MMVPackageInterface.get_ffmpeg_wrapper]"
        from mmv.sombrero.sombrero_ffmpeg import SombreroFFmpegWrapper
        logging.info(f"{debug_prefix} Return SombreroFFmpegWrapper")
        return SombreroFFmpegWrapper(ffmpeg_bin = self.externals.find_binary("ffmpeg"))
    
    # # Audio sources

    # Real time, reads from a loopback device
    def get_audio_source_realtime(self):
        debug_prefix = "[MMVPackageInterface.get_audio_source_realtime]"
        from mmv.common.cmn_audio import AudioSourceRealtime
        return AudioSourceRealtime()

    # File source, used for headless rendering    
    def get_audio_source_file(self):
        debug_prefix = "[MMVPackageInterface.get_audio_source_file]"
        from mmv.common.cmn_audio import AudioSourceFile
        return AudioSourceFile(ffmpeg_wrapper = self.get_ffmpeg_wrapper())

    # Main interface class, mainly sets up root dirs, get config, distributes classes
    # Send platform = "windows", "macos", "linux" for forcing a specific one
    def __init__(self, platform = None, **kwargs) -> None:
        debug_prefix = "[MMVPackageInterface.__init__]"

        self.version = "4.0: Sombrero"

        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_interface.MMV_PACKAGE_ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.MMV_PACKAGE_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
            print(f"{debug_prefix} Running directly from source code")
        else:
            self.MMV_PACKAGE_ROOT = Path(os.path.dirname(os.path.abspath(sys.executable)))
            print(f"{debug_prefix} Running from release (sys.executable..?)")

        print(f"{debug_prefix} Modular Music Visualizer Python package [__init__.py] or executable located at [{self.MMV_PACKAGE_ROOT}]")

        # Classes
        self.utils = Utils()

        # # Load config
        config_file = self.MMV_PACKAGE_ROOT / "config.toml"
        self.config = self.utils.load_yaml(self.MMV_PACKAGE_ROOT / "config.yaml")
        print(f"{debug_prefix} Loaded config configuration file, data: [{self.config}]")

        # # # Logging 

        # Get logger and empty the list
        logger = logging.getLogger()
        logger.handlers = []

        # Handlers on logging to file and shell output, the first one if the user says to
        handlers = [logging.StreamHandler(sys.stdout)]

        # Loglevel is defined in the config.toml configuration
        LOG_LEVEL = {
            "critical": logging.CRITICAL,
            "debug": logging.DEBUG,
            "error": logging.ERROR,
            "info": logging.INFO,
            "warn": logging.warning,
            "notset": logging.NOTSET,
        }.get(self.config["logging"]["log_level"])

        # If user chose to log to a file, add its handler..
        if self.config["logging"]["log_to_file"]:

            # Hard coded where the log file will be located
            # this is only valid for the last time we run this software
            self.LOG_FILE = self.MMV_PACKAGE_ROOT / "last_log.log"

            # Reset the log file
            self.LOG_FILE.write_text("")
            print(f"{debug_prefix} Reset log file located at [{self.LOG_FILE}]")

            # Verbose and append the file handler
            handlers.append(logging.FileHandler(filename = self.LOG_FILE, encoding = 'utf-8'))

        # .. otherwise just keep the StreamHandler to stdout

        log_format = {
            "informational": "[%(levelname)-8s] [%(filename)-32s:%(lineno)-3d] (%(relativeCreated)-6d) %(message)s",
            "pretty": "[%(levelname)-8s] (%(relativeCreated)-5d)ms %(message)s",
            "economic": "[%(levelname)s::%(filename)s::%(lineno)d] %(message)s",
            "onlymessage": "%(message)s"
        }.get(self.config["logging"]["log_format"])

        # Start the logging global class, output to file and stdout
        logging.basicConfig(
            level = LOG_LEVEL,
            format = log_format,
            handlers = handlers,
        )

        # Greeter message :)
        self.greeter_message()

        # Start logging message
        bias = " " * ((self.terminal_width//2) - 13);
        print(f"{bias[:-1]}# # [ Start Logging ] # #\n")
        print("-" * self.terminal_width + "\n")

        # Log what we'll do next
        logging.info(f"{debug_prefix} We're done with the pre configuration of Python's behavior and loading config.toml configuration file")

        # Log precise Python version
        sysversion = sys.version.replace("\n", " ").replace("  ", " ")
        logging.info(f"{debug_prefix} Running on Python: [{sysversion}]")

        # # The operating system we're on, one of "linux", "windows", "macos"

        # Get the desired name from a dict matching against os.name
        if platform is None:
            self.os = {
                "posix": "linux",
                "nt": "windows",
                "darwin": "macos"
            }.get(os.name)
        else:
            logging.info(f"{debug_prefix} Overriding platform OS to = [{platform}]")
            self.os = platform

        # Log which OS we're running
        logging.info(f"{debug_prefix} Running Modular Music Visualizer on Operating System: [{self.os}]")

        # # Create interface's classes

        logging.info(f"{debug_prefix} Creating Download() class")
        self.download = Download()
        self.shaders_cli = None

        # # Common directories between packages

        # Downloads (inside externals)
        self.downloads_dir = self.MMV_PACKAGE_ROOT / "externals" / "downloads"
        self.downloads_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Downloads dir is [{self.downloads_dir}]")

        # Data dir
        self.data_dir = self.MMV_PACKAGE_ROOT / "data"
        self.data_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Data dir is [{self.data_dir}]")

        # Shaders dir
        self.shaders_dir = self.MMV_PACKAGE_ROOT / "shaders"
        self.shaders_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Shaders dir is [{self.shaders_dir}]")

        # Sombrero dir
        self.sombrero_dir = self.MMV_PACKAGE_ROOT / "sombrero"
        logging.info(f"{debug_prefix} Sombrero dir is [{self.sombrero_dir}]")

        # Assets dir
        self.assets_dir = self.shaders_dir / "assets"
        self.assets_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Assets dir is [{self.assets_dir}]")

        # Screenshots dir
        self.screenshots_dir = self.MMV_PACKAGE_ROOT / "screenshots"
        self.screenshots_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Shaders dir is [{self.screenshots_dir}]")

        # Renders dir
        self.renders_dir = self.MMV_PACKAGE_ROOT / "renders"
        self.renders_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Renders dir is [{self.shaders_dir}]")

        # Runtime dir
        self.runtime_dir = self.MMV_PACKAGE_ROOT / "runtime"
        logging.info(f"{debug_prefix} Runtime dir is [{self.runtime_dir}], deleting..")
        shutil.rmtree(self.runtime_dir, ignore_errors = True)
        self.runtime_dir.mkdir(parents = True, exist_ok = True)

        # NOTE: Extend this package interface with the externals manager
        self.externals = ExternalsManager(self)
