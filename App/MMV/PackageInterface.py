"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

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
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import toml
from appdirs import AppDirs
from dotmap import DotMap
from MMV.Common.ExternalsManager import ExternalsManager
from MMV.Common.Utils import Utils
from MMV.Editor import mmvEditor
from MMV.Sombrero.SombreroFFmpeg import SombreroFFmpegWrapper

# from MMV.Sombrero.SombreroMain import SombreroMain

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
        return SombreroMain

    # Return one (usually required) setting up encoder unless using preview window
    def GetFFmpegWrapper(self):
        dpfx = "[mmvPackageInterface.GetFFmpegWrapper]"
        logging.info(f"{dpfx} Return SombreroFFmpegWrapper")
        return SombreroFFmpegWrapper(ffmpeg_bin = self.FFmpegBinary)

    # Main interface class, mainly sets up root dirs, get config, distributes classes
    # Send ForcePlatform = "Windows", "MacOS", "Linux" for forcing a specific one
    def __init__(self, ForcePlatform=None, **kwargs) -> None:
        dpfx = "[mmvPackageInterface.__init__]"
        self.VersionNumber = "4.1.2"
        self.Version = f"{self.VersionNumber}: Node Editor"

        # Detect if we are running from a release or from source code
        if globals().get("__compiled__", None) is not None:
            self.DIR = Path(sys.argv[0]).resolve().parent
            print(f"{dpfx} Running from Nuitka compiled binary")
            self.IS_RELEASE = True
        else:
            self.DIR = Path(os.path.dirname(os.path.abspath(__file__)))
            self.IS_RELEASE = False
            print(f"{dpfx} Running directly from source code")
        print(f"{dpfx} Modular Music Visualizer Python package [__init__.py] or executable located at [{self.DIR}]")

        # Platform Dirs
        self.AppName = "ModularMusicVisualizer"
        self.AppAuthor = "MMV"
        self.AppDirs = AppDirs(self.AppName, self.AppAuthor)
        self.AppDirsVersioned = AppDirs(self.AppName, self.AppAuthor, version=self.VersionNumber)

        # The most important directory, where we also load startup configuration
        self.DataDir = self.DIR/"Data"

        # Config
        self.ConfigYAML = DotMap( Utils.LoadYaml(self.DataDir/"Config.yaml"), _dynamic=False )
        logging.info(f"Config YAML is {self.ConfigYAML}")

        # # # Logging 

        # Get logger and empty the list
        logger = logging.getLogger()
        logger.handlers = []

        # Handlers on logging to file and shell output, the first one if the user says to
        handlers = [logging.StreamHandler(sys.stdout)]

        # Loglevel is defined in the config.toml configuration
        LogLevel = {
            "Critical": logging.CRITICAL,
            "Debug": logging.DEBUG,
            "Error": logging.ERROR,
            "Info": logging.INFO,
            "Warn": logging.warning,
            "NotSet": logging.NOTSET,
        }.get(self.ConfigYAML.Logging.LogLevel)

        # Where to log, reset file
        self.LOG_FILE = self.DIR/"LastLog.txt"
        self.LOG_FILE.write_text("")
        print(f"{dpfx} Reset log file located at [{self.LOG_FILE}]")

        # Verbose and append the file handler
        handlers.append(logging.FileHandler(filename=self.LOG_FILE, encoding='utf-8'))

        # .. otherwise just keep the StreamHandler to stdout
        LogFormat = {
            "Informational": "[%(levelname)-8s] [%(filename)-32s:%(lineno)-3d] (%(relativeCreated)-6d) %(message)s",
            "Pretty": "[%(levelname)-8s] (%(relativeCreated)-5d)ms %(message)s",
            "Economic": "[%(levelname)s::%(filename)s::%(lineno)d] %(message)s",
            "Onlymessage": "%(message)s"
        }.get(self.ConfigYAML.Logging.LogFormat)

        # Start the logging global class, output to file and stdout
        logging.basicConfig(level=LogLevel, format=LogFormat, handlers=handlers)
        self.GreeterMessage()

        # Start logging message
        bias = " " * ((self.terminal_width//2) - 13);
        print(f"{bias[:-1]}# # [ Start Logging ] # #\n")
        print("-" * self.terminal_width + "\n")

        # Log precise Python version
        sysversion = sys.version.replace("\n", " ").replace("  ", " ")
        if self.ConfigYAML.Logging.Privacy.LogPythonVersion:
            logging.info(f"{dpfx} Running on Python: [{sysversion}]")

        # Optional System Info logging
        SystemInfo = platform.uname()
        if self.ConfigYAML.Logging.Privacy.LogBasicSystemInfo:
            logging.info(f"{dpfx} Host System Info:")
            logging.info(f"{dpfx} | Platform:   [{SystemInfo.system}]")
            logging.info(f"{dpfx} | Release:    [{SystemInfo.release}]")
            if SystemInfo.system != "Linux":
                logging.info(f"{dpfx} | Version:    [{SystemInfo.version}]")
            logging.info(f"{dpfx} | Arch:       [{SystemInfo.machine}]")
            logging.info(f"{dpfx} | CPU, Cores: [{SystemInfo.processor}]")

        # Get the desired name from a dict matching against os.name
        if ForcePlatform is None:
            self.os = Utils.GetOS()
        else:
            logging.info(f"{dpfx} Overriding platform OS to = [{ForcePlatform}]")
            self.os = ForcePlatform
        logging.info(f"{dpfx} Running Modular Music Visualizer on Operating System: [{self.os}]")

        # # Directories

        # NOTE: Extend this package interface with the externals manager
        self.Externals = ExternalsManager(self)

        # Set up directories
        self.ScreenshotsDir = self.DIR/"Screenshots"
        self.RendersDir     = self.DIR/"Renders"
        self.RuntimeDir     = self.DIR/"Runtime"
        self.TempDir        = self.DIR/"Runtime"/"Temp"
        self.NodesDir       = self.DataDir/"Nodes"
        self.ImageDir       = self.DataDir/"Image"
        self.ShadersDir     = self.DataDir/"Shaders"
        self.SombreroDir    = self.ShadersDir/"Sombrero"
        self.AssetsDir      = self.DataDir/"Assets"
        self.FontsDir       = self.DataDir/"Fonts"
        self.IconDir        = self.ImageDir/"Icon"
        self.DownloadsDir   = self.Externals.ExternalsDir/"Downloads"

        # mkdirs, print where they are
        for key, value in self.__dict__.items():
            if key.endswith("Dir"):
                logging.info(f"{dpfx} {key} is [{value}]")
                getattr(self, key).mkdir(parents=True, exist_ok=True)

        # Get all stuff we will use, mostly for checking if we have them
        self.FindExternals()
        
    def FindExternals(self):
        # Get the binaries
        self.FFmpegBinary = Utils.FindBinary("ffmpeg")
        self.FFplayBinary = Utils.FindBinary("ffplay")
