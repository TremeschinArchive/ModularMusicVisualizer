"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Manage externals (FFmpeg on Windows, download soundfonts)

NOTE: Extends MMVPackageInterface

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
import logging
import sys

import os


class ExternalsManager:
    def __init__(self, mmv_package_interface):
        debug_prefix = "[ExternalsManager.__init__]"
        self.mmv_package_interface = mmv_package_interface
        self.__dict__ = self.mmv_package_interface.__dict__

        # Externals
        self.externals_dir = self.MMV_PACKAGE_ROOT / "externals"
        self.externals_dir.mkdir(parents = True, exist_ok = True)
        logging.info(f"{debug_prefix} Externals dir is [{self.externals_dir}]")

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

        # Windoe juuuust in case
        if self.os == "windows":
            logging.info(f"{debug_prefix} Appending the Externals directory to system path juuuust in case...")
            sys.path.append(self.externals_dir)

        # Update the externals search path (create one in this case)
        self.update_externals_search_path()

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
        if externals_subdirs: self.EXTERNALS_SEARCH_PATH += externals_subdirs

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
    # Possible values for target are: ["ffmpeg", "musescore"]
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

        logging.warning(f"{debug_prefix} You are using Linux or macOS, please make sure you have [{binary}] package binary installed on your distro or on homebrew, we'll just check for it now, can't continue if you don't have it..")
        
        # Can't continue
        if not self.find_binary(binary):
            logging.error(f"{debug_prefix} Couldn't find lowercase [{binary}] binary on PATH, install from your Linux distro package manager / macOS homebrew, please install it")

            # Log any extra help we give the user
            if help_fix is not None:
                logging.error(f"{debug_prefix} {help_fix}")

            # Exit with non zero error code
            sys.exit(-1)
    