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

import mmv.common.cmn_any_logger
from pyunpack import Archive
from tqdm import tqdm
import requests
import zipfile
import logging
import time
import wget
import sys
import os


class Download:

    def wget_progress_bar(self, current, total, width=80):
        # current         \propto time.time() - startdownload 
        # total - current \propto eta
        # eta = (total-current)*(time.time()-startdownload)) / current

        try: # div by zero
            eta = int(( (time.time() - self.start) * (total - current) ) / current)
        except Exception:
            eta = 0

        avgdown = ( current / (time.time() - self.start) ) / 1024

        currentpercentage = int(current / total * 100)
        
        print("\r Downloading file [{}]: [{}%] [{:.2f} MB / {:.2f} MB] ETA: [{} sec] AVG: [{:.2f} kB/s]".format(self.download_name, currentpercentage, current/1024/1024, total/1024/1024, eta, avgdown), end='', flush=True)

    def wget(self, url, save, name="Undefined"):
        debug_prefix = "[Download.wget]"

        self.download_name = name
        self.start = time.time()

        print(debug_prefix, f"Get file from URL [{url}] saving to [{save}]")

        if os.path.exists(save):
            print(debug_prefix, f"Download file already exists, skipping")
            return

        wget.download(url, save, bar=self.wget_progress_bar)
        print()
    
    # Get html content
    def get_html_content(self, url):
        debug_prefix = "[Download.get_html_content]"

        print(debug_prefix, f"Getting content from [{url}]")

        r = requests.get(url)
        return r.text

    # Extract a compressed file
    def extract_file(self, src, dst):
        debug_prefix = "[Download.extract_file]"
        print(debug_prefix, f"Extracing [{src}] -> [{dst}]")

        Archive(src).extractall(dst)
    
    def extract_zip(self, src, dst):
        with zipfile.ZipFile(src, 'r') as zipped:
            zipped.extractall(dst)