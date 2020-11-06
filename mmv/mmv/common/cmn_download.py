"""
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

from pyunpack import Archive
from tqdm import tqdm
import requests
import zipfile
import time
import wget
import git
import sys
import os


class Download:

    def git_clone(self, url, save):
        # For getting the repo name, if it ends on / we can't
        # split and get the last split of "/" o we shorten it by one
        if url.endswith("/"):
            url = url[0:-1]

        self.repo_name = url.split("/")[-1]
        print(f"Clone repo [{self.repo_name}] from url [{url}] saving to [{save}]")
        try:
            git.Repo.clone_from(url, save, progress=self.git_clone_progress_bar)
            print()
        except git.exc.GitCommandError:
            print(f"Could not clone repo")
            if os.path.exists(save):
                print(f"Repo folder already exists, continuing (consider deleting it if something goes wrong)")
            else:
                print(f"Repo folder doesn't exist and can't clone")
                sys.exit(-1)
        
    def git_clone_progress_bar(self, _, current, total, speed):
        percentage = (current/total)*100
        print(f"\r Cloning repo [{self.repo_name}] | {percentage:0.2f}% | {speed}", end='', flush=True)

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