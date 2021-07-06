"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Manage externals (FFmpeg on Windows, download soundfonts)

NOTE: Extends mmvPackageInterface

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
import os
import sys

import ujson as json
from dotmap import DotMap

from mmv.Common.Download import Download
from mmv.Common.Utils import Utils


class AvailableExternals:
    FFmpeg = "FFmpeg"
    ListOfAll = [FFmpeg]


class ExternalsManager:
    def __init__(self, PackageInterface):
        dpfx = "[ExternalsManager.__init__]"
        self.__dict__ = PackageInterface.__dict__

        # Directories
        self.ExternalsDir          = self.DIR/"Externals"
        self.ExternalsDirDownloads = self.ExternalsDir/"Downloads"
        self.ExternalsDirLinux     = self.ExternalsDir/"Linux"
        self.ExternalsDirWindows   = self.ExternalsDir/"Windows"
        self.ExternalsDirMacOS     = self.ExternalsDir/"MacOS"

        # mkdirs, print where they are
        for key, value in self.__dict__.items():
            if key.startswith("ExternalsDir"):
                logging.info(f"{dpfx} {key} is [{value}]")
                getattr(self, key).mkdir(parents=True, exist_ok=True)

        self.AvailableExternals = AvailableExternals
        self.AssertExternalsInPath()

    # Add externals directory to PATH recursively
    def AssertExternalsInPath(self):
        for dir in Utils.AllSubdirectories(self.ExternalsDirThisPlatform):
            if not str(dir) in sys.path: sys.path.append(str(dir))

    # Get the target externals dir for this platform
    @property
    def ExternalsDirThisPlatform(self):
        return {
            "Linux": self.ExternalsDirLinux,
            "Windows": self.ExternalsDirWindows,
            "MacOS": self.ExternalsDirMacOS,
        }.get(self.os)

    # Download a external from somewhere, extract, put on right path
    def DownloadInstallExternal(self, TargetExternal, Callback=None, _ForceNotFound=False):
        dpfx = "[ExternalsManager.DownloadInstallExternal]"
        logging.info(f"{dpfx} Managing external [{TargetExternal}]")

        if TargetExternal == AvailableExternals.FFmpeg:
            if not Utils.FindBinary("ffmpeg") or _ForceNotFound:
                if self.os == "MacOS": raise RuntimeError("Please install [ffmpeg] package from Homebrew.")
                Info = (
                    "We are downloading FFmpeg, (\"A complete, cross-platform solution to record, "
                    "convert and stream audio and video.\", https://ffmpeg.org/). it is responsible "
                    "for encoding the final videos, reading audio file streams. Fundamental for MMV")
                logging.info(f"{dpfx} {Info}")

                # BtbN FFmpeg build FTW!!
                FFmpegBuilds = json.loads(Download.GetHTMLContent(
                    "https://api.github.com/repos/BtbN/FFmpeg-Builds/releases/latest"))

                # Parsing the version we target and want
                for Asset in FFmpegBuilds["assets"]:
                    AssetName = Asset["name"]

                    WantInName = ["lgpl", "N"]
                    DontWantInName = ["shared"]

                    if self.os == "Linux": WantInName += ["linux64"]
                    if self.os == "Windows": WantInName += ["win64", ".zip"]
                    DownloadURL = None

                    WantOK = all([thing in AssetName for thing in WantInName])
                    DontWantOK = not all([thing in AssetName for thing in DontWantInName])

                    # We have a match!
                    if WantOK and DontWantOK:
                        logging.info(f"{dpfx} We have a match, [{AssetName}]")
                        DownloadURL = Asset["browser_download_url"]
                        break

                if DownloadURL is None: raise RuntimeError("Couldn't match a version of FFmpeg to download")
                        
                # Download the ZIP, extract
                FFmpegZIP = str(self.ExternalsDirDownloads/AssetName)
                SavePath, Status = Download.DownloadFile(URL=DownloadURL, SavePath=FFmpegZIP, Name=f"FFmpeg v={AssetName}", Info=Info, Callback=Callback)
                Status.Info = "Extracting file.."
                Callback(Status)
                Download.ExtractFile(FFmpegZIP, self.ExternalsDirThisPlatform)
            else:
                logging.info(f"{dpfx} Already have external [{TargetExternal}]!!")

        # Update the externals search path because we downloaded stuff
        self.AssertExternalsInPath()
        return True
