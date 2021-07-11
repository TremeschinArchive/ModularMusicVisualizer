"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Downloading files, extracting stuff utilities

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
import tarfile
import time
import zipfile
from pathlib import Path

import arrow
import MMV.Common.AnyLogger
import requests
from dotmap import DotMap
from MMV.Common.Polyglot import Polyglot
from tqdm import tqdm

Speak = Polyglot.Speak


class Download:

    @staticmethod
    def GetHTMLContent(URL):
        logging.info(f"[Download.GetHTMLContent] Getting content from [{URL}]")
        return requests.get(URL).text

    # Download some file to a SavePath (file).
    @staticmethod
    def DownloadFile(URL, SavePath, Name="Downloading File", Locale="en-us", CheckSizes=True, Callback=None, ChunkSize=32768, Info=""):
        if Callback is None: Callback = lambda _:_

        # Set up save path
        SavePath = Path(SavePath).expanduser().resolve()
        SavePath.parent.mkdir(exist_ok=True)

        Status = DotMap(_dynamic=False)
        Status.SavePath = SavePath
        Status.Downloaded = 0
        Status.Completed = 0
        Status.Name = Name
        Status.Info = Info

        logging.info(f"[Download.DownloadFile] Downloading [{Name}]: [{URL}] => [{SavePath}]")
        Status.Info = f"Downloading [{Name}]"; Callback(Status)

        if not CheckSizes:
            if SavePath.exists():
                return SavePath, Status

        # Get info on download, we gotta make sure its target size is the same as already downloaded
        # one if the file existed prior to this, this means incomplete download
        DownloadStream = requests.get(URL, stream=True)
        FileSize = int(DownloadStream.headers.get('content-length', 0))

        if SavePath.exists():
            DownloadedSize = SavePath.stat().st_size
            if DownloadedSize == FileSize:
                logging.info(f"[Download.DownloadFile] Download [{Name}] Already exists [{SavePath}]")
                Status.Info = f"Download already exists and looks good!! Extracting again.."
                Status.Completed = 1; Callback(Status)
                return SavePath, Status
            else:
                Status.Info = f"Incomplete Download, need redownload"; Callback(Status)
                logging.info(f"[Download.DownloadFile] Download [{Name}] Existed in [{SavePath}] but sizes differ [{DownloadedSize}/{FileSize}], redownloading..")
            
        # Progress bar in bits scale
        ProgressBar = tqdm(desc=f"Downloading [{Name}]", total=FileSize, unit='iB', unit_scale=True)

        # Context status
        Status.FileSize = FileSize
        Start = time.time()

        # Open, keep reading
        with open(SavePath, 'wb') as DownloadedFile:
            for NewDataChunk in DownloadStream.iter_content(ChunkSize):
                N = len(NewDataChunk)
                Status.Downloaded += N
                Status.Completed = Status.Downloaded/Status.FileSize
                # Downloaded \/ Took
                # Remaining  /\ ETA
                Took = time.time() - Start
                Remaining = Status.FileSize - Status.Downloaded
                ETA = (Remaining*Took) / (Status.Downloaded+1)
                ETA = arrow.utcnow().shift(seconds=ETA).humanize(locale=Locale)
                Status.Info = Speak("Progress") + f" ({ETA}) [{Status.Downloaded/1024/1024:.2f}M/{Status.FileSize/1024/1024:.2f}M] [{Status.Completed*100:.2f}%]"
                ProgressBar.update(N)
                DownloadedFile.write(NewDataChunk)
                Callback(Status)
        Status.Completed = 1
        Status.Completed = 1
        Callback(Status)
        ProgressBar.close()
        return SavePath, Status

    # Extract one zip, tar file to a target directory, more like attempt to do so
    def ExtractFile(PackedFile, UnpackDir):
        logging.info(f"[Download.ExtractFile] Extract file [{PackedFile}] => [{UnpackDir}]")

        # Is it a zip?
        try:
            with zipfile.ZipFile(PackedFile, 'r') as ZippedFile:
                ZippedFile.extractall(UnpackDir)
            return
        except zipfile.BadZipFile: pass

        # Is it a tar?
        try:
            with tarfile.open(PackedFile) as TarFile:
                TarFile.extractall(UnpackDir)
            return
        except Exception: pass

        raise RuntimeError(f"No idea how to extract [{PackedFile}]")

