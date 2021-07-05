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

import requests
from dotmap import DotMap
from tqdm import tqdm

import mmv.Common.AnyLogger


class Download:

    @staticmethod
    def GetHTMLContent(URL):
        logging.info(f"[Download.GetHTMLContent] Getting content from [{URL}]")
        return requests.get(URL).text

    # Download some file to a SavePath (file).
    def DownloadFile(URL, SavePath, Name="Downloading File", CheckSizes=True, Callback=lambda _:_, ChunkSize=32768, Info=""):

        # Set up save path
        SavePath = Path(SavePath).expanduser().resolve()
        SavePath.parent.mkdir(exist_ok=True)

        logging.info(f"[Download.DownloadFile] Downloading [{Name}]: [{URL}] => [{SavePath}]")

        if not CheckSizes:
            if SavePath.exists():
                return SavePath

        # Get info on download, we gotta make sure its target size is the same as already downloaded
        # one if the file existed prior to this, this means incomplete download
        DownloadStream = requests.get(URL, stream=True)
        FileSize = int(DownloadStream.headers.get('content-length', 0))

        if SavePath.exists():
            DownloadedSize = SavePath.stat().st_size
            if DownloadedSize == FileSize:
                logging.info(f"[Download.DownloadFile] Download [{Name}] Already exists [{SavePath}]")
                return SavePath
            else:
                logging.info(f"[Download.DownloadFile] Download [{Name}] Existed in [{SavePath}] but sizes differ [{DownloadedSize}/{FileSize}], redownloading..")
            
        # Progress bar in bits scale
        ProgressBar = tqdm(desc=f"Downloading [{Name}]", total=FileSize, unit='iB', unit_scale=True)

        # Context status
        Status = DotMap(_dynamic=False)
        Status.FileSize = FileSize
        Status.SavePath = SavePath
        Status.Downloaded = 0
        Status.Name = Name
        Status.Info = Info

        # Open, keep reading
        with open(SavePath, 'wb') as DownloadedFile:
            for NewDataChunk in DownloadStream.iter_content(ChunkSize):
                Status.Downloaded += len(NewDataChunk)
                ProgressBar.update(len(NewDataChunk))
                DownloadedFile.write(NewDataChunk)
                Callback(Status)

        ProgressBar.close()
        return SavePath

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

