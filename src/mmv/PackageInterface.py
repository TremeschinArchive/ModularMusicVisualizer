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

from mmv.Common.Download import Download
from mmv.Common.ExternalsManager import ExternalsManager
from mmv.Common.Utils import Utils
from mmv.Editor import mmvEditor
from mmv.Sombrero.SombreroFFmpeg import SombreroFFmpegWrapper

# from mmv.Sombrero.SombreroMain import SombreroMGL

sys.dont_write_bytecode = True

# Class that distributes MMV packages, sets up logging and behavior;
class mmvPackageInterface:

    # Hello world!
    def GreeterMessage(self) -> None:
        dpfx = "[mmvPackageInterface.GreeterMessage]"

        # Get a bias for printing the message centered
        self.terminal_width = shutil.get_terminal_size()[0]
        bias = " "*(math.floor(self.terminal_width/2) - 14)

        message = \
f"""{dpfx} Show greeter message\n{"-"*self.terminal_width}
{bias} __  __   __  __  __     __
{bias}|  \\/  | |  \\/  | \\ \\   / /
{bias}| |\\/| | | |\\/| |  \\ \\ / / 
{bias}| |  | | | |  | |   \\ V /  
{bias}|_|  |_| |_|  |_|    \\_/   
{bias}
{bias} Modular Music Visualizer                      
{(2 + int( (self.terminal_width/2) - (len("Version") + len(self.Version)/2) ))*" "}Version {self.Version}
{"-"*self.terminal_width}
"""
        logging.info(message)

    # Thanks message with some official links, warnings
    def ThanksMessage(self):
        dpfx = "[mmvPackageInterface.ThanksMessage]"

        # Get a bias for printing the message centered
        self.terminal_width = shutil.get_terminal_size()[0]
        bias = " "*(math.floor(self.terminal_width/2) - 45)

        message = \
f"""{dpfx} Show thanks message
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

    def GetEditor(self):
        return mmvEditor(self)

    def GetSombrero(self, **kwargs):
        self.___printshadersmode()
        return SombreroMGL

    # Return one (usually required) setting up encoder unless using preview window
    def GetFFmpegWrapper(self):
        dpfx = "[mmvPackageInterface.GetFFmpegWrapper]"
        logging.info(f"{dpfx} Return SombreroFFmpegWrapper")
        return SombreroFFmpegWrapper(ffmpeg_bin = self.FFmpegBinary)

    # Main interface class, mainly sets up root dirs, get config, distributes classes
    # Send ForcePlatform = "Windows", "MacOS", "Linux" for forcing a specific one
    def __init__(self, ForcePlatform=None, **kwargs) -> None:
        dpfx = "[mmvPackageInterface.__init__]"
        self.VersionNumber = "4.1"
        self.Version = f"{self.VersionNumber}: Node Editor"

        # # Where this file is located, please refer using this on the whole package
        # # Refer to it as self.mmv_interface.DIR at any depth in the code
        # # This deals with the case we used pyinstaller and it'll get the executable path instead
        # print("Compiled", globals().get("__compiled__", None))
        # if getattr(sys, 'frozen', True) or (globals().get("__compiled__", None) is not None):    
        #     self.DIR = Path(os.path.dirname(os.path.abspath(__file__)))
        #     print(f"{dpfx} Running directly from source code")
        # else:
        #     self.DIR = Path(os.path.dirname(os.path.abspath(__file__)))
        #     # self.DIR = Path(os.path.dirname(os.path.abspath(sys.executable)))
        #     print(f"{dpfx} Running from release (sys.executable..?)")

        if globals().get("__compiled__", None) is not None:
            self.DIR = Path(sys.argv[0]).resolve().parent
            print(f"{dpfx} Running from Nuitka compiled binary")
            self.IS_RELEASE = True
        else:
            self.DIR = Path(os.path.dirname(os.path.abspath(__file__)))
            self.IS_RELEASE = False
            print(f"{dpfx} Running directly from source code")

        print(f"{dpfx} Modular Music Visualizer Python package [__init__.py] or executable located at [{self.DIR}]")

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
        }.get("info")

        # Hard coded where the log file will be located
        # this is only valid for the last time we run this software
        self.LOG_FILE = self.DIR / "LastLog.txt"

        # Reset the log file
        self.LOG_FILE.write_text("")
        print(f"{dpfx} Reset log file located at [{self.LOG_FILE}]")

        # Verbose and append the file handler
        handlers.append(logging.FileHandler(filename = self.LOG_FILE, encoding = 'utf-8'))

        # .. otherwise just keep the StreamHandler to stdout

        log_format = {
            "informational": "[%(levelname)-8s] [%(filename)-32s:%(lineno)-3d] (%(relativeCreated)-6d) %(message)s",
            "pretty": "[%(levelname)-8s] (%(relativeCreated)-5d)ms %(message)s",
            "economic": "[%(levelname)s::%(filename)s::%(lineno)d] %(message)s",
            "onlymessage": "%(message)s"
        }.get("pretty")

        # Start the logging global class, output to file and stdout
        logging.basicConfig(
            level = LOG_LEVEL,
            format = log_format,
            handlers = handlers,
        )

        # Greeter message :)
        self.GreeterMessage()

        # Start logging message
        bias = " " * ((self.terminal_width//2) - 13);
        print(f"{bias[:-1]}# # [ Start Logging ] # #\n")
        print("-" * self.terminal_width + "\n")

        # Log what we'll do next
        logging.info(f"{dpfx} We're done with the pre configuration of Python's behavior and loading config.toml configuration file")

        # Log precise Python version
        sysversion = sys.version.replace("\n", " ").replace("  ", " ")
        logging.info(f"{dpfx} Running on Python: [{sysversion}]")

        # # The operating system we're on, one of "linux", "windows", "macos"

        # Get the desired name from a dict matching against os.name
        if ForcePlatform is None:
            self.os = Utils.GetOS()
        else:
            logging.info(f"{dpfx} Overriding platform OS to = [{ForcePlatform}]")
            self.os = ForcePlatform

        # Log which OS we're running
        logging.info(f"{dpfx} Running Modular Music Visualizer on Operating System: [{self.os}]")

        # # Directories

        # NOTE: Extend this package interface with the externals manager
        self.Externals = ExternalsManager(self)
        self.Download = Download

        # Set up directories
        self.DataDir        = self.DIR/"Data"
        self.ScreenshotsDir = self.DIR/"Screenshots"
        self.RendersDir     = self.DIR/"Renders"
        self.RuntimeDir     = self.DIR/"Runtime"
        self.NodesDir       = self.DataDir/"Nodes"
        self.ImageDir       = self.DataDir/"Image"
        self.ShadersDir     = self.DataDir/"Shaders"
        self.AssetsDir      = self.DataDir/"Assets"
        self.DownloadsDir   = self.Externals.ExternalsDir/"Downloads"

        # mkdirs, print where they are
        for key, value in self.__dict__.items():
            if key.endswith("Dir"):
                logging.info(f"{dpfx} {key} is [{value}]")
                getattr(self, key).mkdir(parents=True, exist_ok=True)

        # Get the binaries
        self.FFmpegBinary = Utils.FindBinary("ffmpeg")
        self.FFplayBinary = Utils.FindBinary("ffplay")
