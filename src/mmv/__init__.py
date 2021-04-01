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
from mmv.common.cmn_download import Download
from mmv.common.cmn_utils import Utils
from pathlib import Path
import subprocess
import tempfile
import logging
import struct
import shutil
import toml
import math
import json
import sys
import os


# Class that distributes MMV packages, sets up logging and behavior;
# This class is distributed as being called "interface" among mmvskia
# and mmvshader packages, which this one have the "prelude" attribute
# which is the dictionary of the file prelude.toml containing
# general behavior of MMV
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

    # Get a moderngl wrapper / interface for rendering fragment shaders, getting their
    # contents, map images, videos and even other shaders into textures
    def get_mmv_shader_mgl(self, **kwargs):
        self.___printshadersmode()
        from mmv.mmvshader.mmv_shader_mgl import MMVShaderMGL
        return MMVShaderMGL

    # Return shader maker interface
    def get_mmv_shader_maker(self, **kwargs):
        self.___printshadersmode()
        from mmv.mmvshader.mmv_shader_maker import MMVShaderMaker
        return MMVShaderMaker

    # Return one (usually required) setting up encoder unless using preview window
    def get_ffmpeg_wrapper(self):
        debug_prefix = "[MMVPackageInterface.get_ffmpeg_wrapper]"
        from mmv.common.wrappers.wrap_ffmpeg import FFmpegWrapper
        logging.info(f"{debug_prefix} Return FFmpegWrapper")
        return FFmpegWrapper(ffmpeg_binary_path = self.find_binary("ffmpeg"))
    
    # Return FFplay wrapper, rarely needed but just in case
    def get_ffplay_wrapper(self):
        debug_prefix = "[MMVPackageInterface.get_ffplay_wrapper]"
        from mmv.common.wrappers.wrap_ffplay import FFplayWrapper
        logging.info(f"{debug_prefix} Return FFplayWrapper")
        return FFplayWrapper()
    
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

    # Real time, reads from a loopback device
    def get_jumpcutter(self):
        debug_prefix = "[MMVPackageInterface.get_jumpcutter]"
        self.terminal_width = shutil.get_terminal_size()[0]
        bias = " "*(math.floor(self.terminal_width/2) - 28)
        message = \
f"""{debug_prefix} Show extension\n{"="*self.terminal_width}
{bias}   ___                       _____       _   _            
{bias}  |_  |                     /  __ \\     | | | |           
{bias}    | |_   _ _ __ ___  _ __ | /  \\/_   _| |_| |_ ___ _ __ 
{bias}    | | | | | '_ ` _ \\| '_ \\| |   | | | | __| __/ _ \\ '__|
{bias}/\\__/ / |_| | | | | | | |_) | \\__/\\ |_| | |_| ||  __/ |   
{bias}\\____/ \\__,_|_| |_| |_| .__/ \\____/\\__,_|\\__|\\__\\___|_|   
{bias}                      | |                                 
{bias}                      |_|                                
{bias}
{bias}                   + MMV Extension +
{"="*self.terminal_width}
"""
        logging.info(message)
        from mmv.extra.extra_jumpcutter import JumpCutter
        return JumpCutter(ffmpeg_wrapper = self.get_ffmpeg_wrapper())

    # Main interface class, mainly sets up root dirs, get config, distributes classes
    # Send platform = "windows", "macos", "linux" for forcing a specific one
    def __init__(self, platform = None, **kwargs) -> None:
        debug_prefix = "[MMVPackageInterface.__init__]"

        self.version = "3.1: rolling"

        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_skia_main.MMV_PACKAGE_ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.MMV_PACKAGE_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))
            print(f"{debug_prefix} Running directly from source code")
        else:
            self.MMV_PACKAGE_ROOT = Path(os.path.dirname(os.path.abspath(sys.executable)))
            print(f"{debug_prefix} Running from release (sys.executable..?)")

        print(f"{debug_prefix} Modular Music Visualizer Python package [__init__.py] or executable located at [{self.MMV_PACKAGE_ROOT}]")

        # # Load prelude configuration

        print(f"{debug_prefix} Loading prelude configuration file")
        
        # Build the path the prelude file should be located at
        prelude_file = self.MMV_PACKAGE_ROOT / "prelude.toml"
        print(f"{debug_prefix} Attempting to load prelude file located at [{prelude_file}], we cannot continue if this is wrong..")

        # Load the prelude file
        with open(prelude_file, "r") as f:
            self.prelude = toml.loads(f.read())
        
        print(f"{debug_prefix} Loaded prelude configuration file, data: [{self.prelude}]")

        # # # Logging 

        # # We can now set up logging as we have where this file is located at

        # # Reset current handlers if any
        print(f"{debug_prefix} Resetting Python's logging logger handlers to empty list")

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
            self.LOG_FILE = self.MMV_PACKAGE_ROOT / "last_log.log"

            # Reset the log file
            with open(self.LOG_FILE, "w") as f:
                print(f"{debug_prefix} Reset log file located at [{self.LOG_FILE}]")
                f.write("")

            # Verbose and append the file handler
            print(f"{debug_prefix} Reset log file located at [{self.LOG_FILE}]")
            handlers.append(logging.FileHandler(filename = self.LOG_FILE, encoding = 'utf-8'))

        # .. otherwise just keep the StreamHandler to stdout

        log_format = {
            "informational": "[%(levelname)-8s] [%(filename)-32s:%(lineno)-3d] (%(relativeCreated)-6d) %(message)s",
            "pretty": "[%(levelname)-8s] (%(relativeCreated)-5d)ms %(message)s",
            "economic": "[%(levelname)s::%(filename)s::%(lineno)d] %(message)s",
            "onlymessage": "%(message)s"
        }.get(self.prelude["logging"]["log_format"])

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
        logging.info(f"{debug_prefix} We're done with the pre configuration of Python's behavior and loading prelude.toml configuration file")

        # Log precise Python version
        sysversion = sys.version.replace("\n", " ").replace("  ", " ")
        logging.info(f"{debug_prefix} Running on Python: [{sysversion}]")

        # # # FIXME: Python 3.9, go home you're drunk

        # Max python version, show info, assert, pretty print
        maximum_working_python_version = (3, 8)
        pversion = sys.version_info

        # Log and check
        logging.info(f"{debug_prefix} Checking if Python <= {maximum_working_python_version} for a working version.. ")

        # Huh we're on Python 2..?
        if pversion[0] == 2:
            logging.error(f"{debug_prefix} Please upgrade to at least Python 3")
            sys.exit(-1)
        
        # Python is ok
        if (pversion[0] <= maximum_working_python_version[0]) and (pversion[1] <= maximum_working_python_version[1]):
            logging.info(f"{debug_prefix} Ok, good python version")
        else:
            # Warn Python 3.9 is a bit unstable, even the developer had issues making it work
            logging.warn(f"{debug_prefix} Python 3.9 is acting a bit weird regarding some dependencies on some systems, while it should be possible to run, take it with some grain of salt and report back into the discussions troubles or workarounds you found?")

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

        logging.info(f"{debug_prefix} Creating Utils() class")
        self.utils = Utils()

        logging.info(f"{debug_prefix} Creating Download() class")
        self.download = Download()

        # # Common directories between packages

        # Externals
        self.externals_dir = self.MMV_PACKAGE_ROOT / "externals"
        self.externals_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Externals dir is [{self.externals_dir}]")

        # Downloads (inside externals)
        self.downloads_dir = self.MMV_PACKAGE_ROOT / "externals" / "downloads"
        self.downloads_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Downloads dir is [{self.downloads_dir}]")

        # Assets dir
        self.assets_dir = self.MMV_PACKAGE_ROOT / "assets"
        self.assets_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Assets dir is [{self.assets_dir}]")

        # Shaders dir
        self.shaders_dir = self.MMV_PACKAGE_ROOT / "shaders"
        self.shaders_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Shaders dir is [{self.shaders_dir}]")

        # Runtime dir
        self.runtime_dir = self.MMV_PACKAGE_ROOT / "runtime"
        logging.info(f"{debug_prefix} Runtime dir is [{self.runtime_dir}], deleting..")
        shutil.rmtree(self.runtime_dir, ignore_errors = True)
        self.runtime_dir.mkdir(parents = True, exist_ok = True)

        # Windoe juuuust in case
        if self.os == "windows":
            logging.info(f"{debug_prefix} Appending the Externals directory to system path juuuust in case...")
            sys.path.append(self.externals_dir)

        # # Common files

        # Code flow management
        if self.prelude["flow"]["stop_at_initialization"]:
            logging.critical(f"{debug_prefix} Exiting as stop_at_initialization key on prelude.toml is True")
            sys.exit(0)
        
        # # External dependencies where to append for PATH

        # Externals directory for Linux
        self.externals_dir_linux = self.MMV_PACKAGE_ROOT / "externals" / "linux"
        if self.os == "linux":
            logging.info(f"{debug_prefix} Externals directory for Linux OS is [{self.externals_dir_linux}]")
            self.externals_dir_linux.mkdir(parents = True, exist_ok = True)

        # Externals directory for Windows
        self.externals_dir_windows = self.MMV_PACKAGE_ROOT / "externals" / "windows"
        if self.os == "windows":
            logging.info(f"{debug_prefix} Externals directory for Windows OS is [{self.externals_dir_windows}]")
            self.externals_dir_windows.mkdir(parents = True, exist_ok = True)

        # Externals directory for macOS
        self.externals_dir_macos = self.MMV_PACKAGE_ROOT / "externals" / "macos"
        if self.os == "macos":
            logging.info(f"{debug_prefix} Externals directory for Darwin OS (macOS) is [{self.externals_dir_macos}]")
            self.externals_dir_macos.mkdir(parents = True, exist_ok = True)

        # # This native platform externals dir
        self.externals_dir_this_platform = self.__get_platform_external_dir(self.os)
        logging.info(f"{debug_prefix} This platform externals directory is: [{self.externals_dir_this_platform}]")

        # Update the externals search path (create one in this case)
        self.update_externals_search_path()

        # Code flow management
        if self.prelude["flow"]["stop_at_initialization"]:
            logging.critical(f"{debug_prefix} Exiting as stop_at_initialization key on prelude.toml is True")
            sys.exit(0)
    
    # Get the target externals dir for this platform
    def __get_platform_external_dir(self, platform):
        debug_prefix = "[MMVPackageInterface.__get_platform_external_dir]"

        # # This platform externals dir
        externals_dir = {
            "linux": self.externals_dir_linux,
            "windows": self.externals_dir_windows,
            "macos": self.externals_dir_macos,
        }.get(platform)

        # mkdir dne just in case cause we asked for this?
        externals_dir.mkdir(parents = True, exist_ok = True)

        # log action
        logging.info(f"{debug_prefix} Return external dir for platform [{platform}] -> [{externals_dir}]")
        return externals_dir

    # Update the self.EXTERNALS_SEARCH_PATH to every recursive subdirectory on the platform's externals dir
    def update_externals_search_path(self):
        debug_prefix = "[MMVPackageInterface.update_externals_search_path]"

        # The subdirectories on this platform externals folder
        externals_subdirs = self.utils.get_recursively_all_subdirectories(self.externals_dir_this_platform)

        # When using some function like Utils.get_executable_with_name, it have an argument
        # called extra_paths, add this for searching for the full externals directory.
        # Preferably use this interface methods like find_binary instead
        self.EXTERNALS_SEARCH_PATH = [self.externals_dir_this_platform]

        # If we do have subdirectories on this platform externals then append to it
        if externals_subdirs:
            self.EXTERNALS_SEARCH_PATH += externals_subdirs

    # Search for something in system's PATH, also searches for the externals folder
    # Don't append the extra .exe because Linux, macOS doesn't have these, returns False if no binary was found
    def find_binary(self, binary):
        debug_prefix = "[MMVPackageInterface.find_binary]"

        # Append .exe for Windows
        if (self.os == "windows") and (not binary.endswith(".exe")):
            binary += ".exe"

        # Log action
        logging.info(f"{debug_prefix} Finding binary in PATH and EXTERNALS directories: [{binary}]")
        return self.utils.get_executable_with_name(binary, extra_paths = self.EXTERNALS_SEARCH_PATH)

    # Make sure we have some target Externals, downloads latest release for them.
    # For forcing to download the Windows binaries for a release, send platform="windows" for overwriting
    # otherwise it'll be set to this class's os.
    #
    # For FFmpeg, mpv: Linux and macOS people please install from your distro's package manager.
    #
    # Possible values for target are: ["ffmpeg", "mpv", "musescore"]
    #
    def check_download_externals(self, target_externals = [], platform = None):
        debug_prefix = "[MMVPackageInterface.check_download_externals]"

        # Overwrite os if user set to a specific one
        if platform is None:
            platform = self.os
        else:
            # Error assertion, only allow linux, macos or windows target os
            valid = ["linux", "macos", "windows"]
            if not platform in valid:
                err = f"Target os [{platform}] not valid: should be one of {valid}"
                logging.error(f"{debug_prefix} {err}")
                raise RuntimeError(err)

        # Force the externals argument to be a list
        target_externals = self.utils.force_list(target_externals)

        # Log action
        logging.info(f"{debug_prefix} Checking externals {target_externals} for os = [{platform}]")

        # We're frozen (running from release..)
        if getattr(sys, 'frozen', False):
            logging.info(f"{debug_prefix} Not checking for externals because is executable build.. (should have them bundled?)")
            return

        # Short hand
        sep = os.path.sep
        
        # The target externals dir for this platform, it must be windows if we're here..
        target_externals_dir = self.__get_platform_external_dir(platform)

        # For each target external
        for external in target_externals:
            debug_prefix = "[MMVPackageInterface.check_download_externals]"
            logging.info(f"{debug_prefix} Checking / downloading external: [{external}] for platform [{platform}]")
            
            # # FFmpeg / FFprobe

            if external == "ffmpeg":
                debug_prefix = f"[MMVPackageInterface.check_download_externals({external})]"

                # We're on Linux / macOS so checking ffmpeg external dependency on system's path
                if platform in ["linux", "macos"]:
                    self.__cant_micro_manage_external_for_you(binary = "ffmpeg")
                    continue
                
                # If we don't have FFmpeg binary on externals dir
                if not self.find_binary("ffmpeg.exe"):

                    # Get the latest release number of ffmpeg
                    repo = "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"
                    logging.info(f"{debug_prefix} Getting latest release info on repository: [{repo}]")
                    ffmpeg_release = json.loads(self.download.get_html_content(repo))

                    # The assets (downloadable stuff)
                    assets = ffmpeg_release["assets"]
                    logging.info(f"{debug_prefix} Available assets to download (checking for non shared, gpl, non vulkan release):")

                    # Parsing the version we target and want
                    for item in assets:

                        # The name of the 
                        name = item["name"]
                        logging.info(f"{debug_prefix} - [{name}]")

                        # Expected stuff
                        is_lgpl = "lgpl" in name
                        is_shared = "shared" in name
                        have_vulkan = "vulkan" in name
                        from_master = "N" in name

                        # Log what we expect
                        logging.info(f"{debug_prefix} - :: Is LGPL:                   [{is_lgpl:<1}] (expect: 0)")
                        logging.info(f"{debug_prefix} - :: Is Shared:                 [{is_shared:<1}] (expect: 0)")
                        logging.info(f"{debug_prefix} - :: Have Vulkan:               [{have_vulkan:<1}] (expect: 0)")
                        logging.info(f"{debug_prefix} - :: Master branch (N in name): [{from_master:<1}] (expect: 0)")

                        # We have a match!
                        if not (is_lgpl + is_shared + have_vulkan + from_master):
                            logging.info(f"{debug_prefix} - >> :: We have a match!!")
                            download_url = item["browser_download_url"]
                            break

                    # Where we'll download from
                    logging.info(f"{debug_prefix} Download URL: [{download_url}]")

                    # Where we'll save the compressed zip of FFmpeg
                    ffmpeg_zip = self.downloads_dir + f"{sep}{name}"

                    # Download FFmpeg build
                    self.download.wget(download_url, ffmpeg_zip, f"FFmpeg v={name}")

                    # Extract the files
                    self.download.extract_zip(ffmpeg_zip, target_externals_dir)

                else:  # Already have the binary
                    logging.info(f"{debug_prefix} Already have [ffmpeg] binary in externals / system path!!")

            # # MPV FIXME: deprecate future version

            if external == "mpv":
                debug_prefix = f"[MMVPackageInterface.check_download_externals({external})]"

                # We're on Linux / macOS so checking ffmpeg external dependency on system's path
                if platform in ["linux", "macos"]:
                    self.__cant_micro_manage_external_for_you(binary = "mpv", help_fix = f"Visit [https://mpv.io/installation/]")
                    continue

                # If we don't have mpv binary on externals dir or system's path
                if not self.find_binary("mpv"):

                    mpv_7z_version = "mpv-x86_64-20201220-git-dde0189.7z"

                    # Where we'll save the compressed zip of FFmpeg
                    mpv_7z = self.downloads_dir + f"{sep}{mpv_7z_version}"

                    # Download mpv build
                    self.download.wget(
                        f"https://sourceforge.net/projects/mpv-player-windows/files/64bit/{mpv_7z_version}/download",
                        mpv_7z, f"MPV v=20201220-git-dde0189"
                    )

                    # Where to extract final mpv
                    mpv_extracted_folder = f"{self.externals_dir_this_platform}{sep}" + mpv_7z_version.replace(".7z", "")
                    self.utils.mkdir_dne(path = mpv_extracted_folder)

                    # Extract the files
                    self.download.extract_file(mpv_7z, mpv_extracted_folder)
               
                else:  # Already have the binary
                    logging.info(f"{debug_prefix} Already have [mpv] binary in externals / system path!!")

            # # Musescore

            if external == "musescore":
                debug_prefix = f"[MMVPackageInterface.check_download_externals({external})]"

                # We're on Linux / macOS so checking ffmpeg external dependency on system's path
                if platform in ["linux", "macos"]:
                    self.__cant_micro_manage_external_for_you(binary = "musescore", help_fix = f"Go to [https://musescore.org/en/download] and install for your platform")
                    continue
                
                # If we don't have musescore binary on externals dir or system's path
                if not self.find_binary("musescore"):

                    # Version we want
                    musescore_version = "v3.5.2/MuseScorePortable-3.5.2.311459983-x86.paf.exe"

                    # Download musescore
                    self.download.wget(
                        f"https://cdn.jsdelivr.net/musescore/{musescore_version}",
                        f"{self.externals_dir_this_platform}{sep}musescore.exe", f"Musescore Portable v=[{musescore_version}]"
                    )
                    
                else:  # Already have the binary
                    logging.info(f"{debug_prefix} Already have [musescore] binary in externals / system path!!")

            # Update the externals search path because we downloaded stuff
            self.update_externals_search_path()

    # Ensure we have an external dependency we can't micro manage because too much entropy
    def __cant_micro_manage_external_for_you(self, binary, help_fix = None):
        debug_prefix = "[MMVPackageInterface.__cant_micro_manage_external_for_you]"

        logging.warn(f"{debug_prefix} You are using Linux or macOS, please make sure you have [{binary}] package binary installed on your distro or on homebrew, we'll just check for it now, can't continue if you don't have it..")
        
        # Can't continue
        if not self.find_binary(binary):
            logging.error(f"{debug_prefix} Couldn't find lowercase [{binary}] binary on PATH, install from your Linux distro package manager / macOS homebrew, please install it")

            # Log any extra help we give the user
            if help_fix is not None:
                logging.error(f"{debug_prefix} {help_fix}")

            # Exit with non zero error code
            sys.exit(-1)
    