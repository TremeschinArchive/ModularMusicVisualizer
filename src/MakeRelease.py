"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Make a MMV release binary targeting a certain platform.

    Host (the one who makes the release):
        Linux:
            - [x] Linux (native, AppImage)
            - [x] Windows (wine, winetricks)
            - [ ] MacOS (prob won't happen)
        Windows:
            - [ ] Windows (TODO)
            - [ ] Linux (Maybe with WSL)
            - [ ] MacOS (lol)
        MacOS:
            - [ ] Windows (maybe wine, untested)
            - [ ] Linux
            - [ ] MacOS (could work, don't have equip to test)

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
import datetime
import os
import shutil
import subprocess
import sys
from distutils.dir_util import copy_tree
from pathlib import Path
from subprocess import PIPE

import mmv

sys.dont_write_bytecode = True

class MakeRelease:
    def __init__(self):
        self.PackageInterface = mmv.mmvPackageInterface()

        # Releases dir
        self.DIR = Path(os.path.dirname(os.path.abspath(__file__)))
        self.ReleasesDir = self.DIR/"Releases"
        self.ReleasesDirLinux = self.ReleasesDir/"Linux"
        self.ReleasesDirWindows = self.ReleasesDir/"Windows"
        self.ReleasesDirMacOS = self.ReleasesDir/"MacOS"
        self.WineprefixDir = Path("~/.mmv").expanduser().resolve()

        # Make Releases dir
        self.ReleasesDir.mkdir(exist_ok=True)

        # Reset paths
        for path in [self.ReleasesDirLinux, self.ReleasesDirWindows, self.ReleasesDirMacOS]:
            if path.exists(): shutil.rmtree(str(path), ignore_errors=True)
            path.mkdir(exist_ok=True)

        self.Target = self.DIR/"RunEditor.py"
        self.TargetBasename = "RunEditor"
        self.Now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.Commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode("utf-8").strip().upper()
        self.ReleaseName = f"Modular Music Visualizer {self.PackageInterface.VersionNumber} [{self.Commit}]"
        self.FinalBinName = "MMV Editor"
        self.Clear()

    def Clear(self):
        # Subprocess vars, env vars
        self.cwd = self.DIR
        self.env = os.environ
    
    def SubprocessRun(self, command):
        print(f"[MakeRelease.SubprocessRun] Run {command}")
        subprocess.run(command, env=self.env, cwd=self.cwd)

    def Rmdir(self, path):
        print(f"[MakeRelease.Rmdir] Remove path [{path}]")
        shutil.rmtree(path, ignore_errors=True)

    def Finish(self, final_zip, path):
        print(f"[MakeRelease.Finish] Zipping target [{path}] => [{final_zip}]")
        ROOT = path.parent
        BASE = path.name
        os.chdir(ROOT)
        where = shutil.make_archive(str(final_zip.name).replace(".zip",""), 'zip', root_dir=ROOT, base_dir=BASE)
        shutil.move(where, final_zip)
        # self.SubprocessRun(["/bin/zip", "-r", "-9", str(final_zip), str(to_compress)])

    # Needs:
    #   git, wine, winetricks
    #
    # Must NOT be in some activated venv when making for Windows
    # Please execute a plain Python bin in this file, if run from poetry it'll always reinstall the deps
    #
    # For making releases for Windows, find a 64bit "mfc42.dll" and put on Externals dir
    #
    def Make(self, platform):
        if platform == "MacOS": raise NotImplementedError("MacOS builds not supported")
        dpfx = "[MakeRelease.Make]"
        self.CurrentMaking = {
            "Linux": self.ReleasesDirLinux,
            "Windows": self.ReleasesDirWindows,
            "MacOS": self.ReleasesDirMacOS
        }[platform]

        self.cwd = self.DIR.parent

        command_prefix = []
        python = "python"
        
        # Windows specific "bootstrap"
        if platform == "Windows":
            WINE = ["wine"]
            WINETRICKS = ["winetricks"]
            command_prefix = WINE
            python = "python.exe"

            # Disable MONO, set WINEPREFIX
            self.env["WINEDLLOVERRIDES"] = "mscoree=d"
            self.env["WINEPREFIX"] = str(self.WineprefixDir)
            self.env["WINEDEBUG"] = "-all"
            self.env["WINEARCH"] = "win64"

            # Create WINEPREFIX
            self.SubprocessRun(WINE + ["wineboot"])
            self.SubprocessRun(WINETRICKS + ["win10"])

            # Download Python
            PYVERSION = "3.9.5"
            python_installer = self.PackageInterface.Download.wget(
                f"https://www.python.org/ftp/python/{PYVERSION}/python-{PYVERSION}-amd64.exe",
                str(self.PackageInterface.Externals.ExternalsDownloadDir/f"Python-{PYVERSION}-AMD64.exe"),
                "Python 3.9.5 Windows 64 bits")
            
            # Install Python
            print(f"{dpfx} Python installed located at [{python_installer}], installing..")
            self.SubprocessRun(WINE + [python_installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"])

            self.SubprocessRun(WINETRICKS + ["--unattended", "mfc42"])
            self.SubprocessRun(WINETRICKS + ["win7"])

        # Install poetry
        self.SubprocessRun(command_prefix + [python, "-m", "pip", "install", "--upgrade", "pip"])
        self.SubprocessRun(command_prefix + [python, "-m", "pip", "install", "poetry", "wheel"])

        # Create venv, install deps
        POETRY = command_prefix + [python, "-m", "poetry"]
        self.SubprocessRun(POETRY + ["install"])

        # Get python binary
        if platform == "Windows": 
            C = self.WineprefixDir/"drive_c"
            shutil.copy(self.PackageInterface.DownloadsDir/"mfc42.dll", C/"windows"/"system32"/"mfc42.dll")

        PYTHON = POETRY + ["run", "python"]

        print(f"{dpfx} Python is {PYTHON}")
        NUITKA = PYTHON + ["-m", "nuitka"]
        PIP = PYTHON + ["-m", "pip"]

        # Install Nuitka
        self.SubprocessRun(PIP + ["install", "--upgrade", "nuitka", "scons", "imageio"])

        icon = self.PackageInterface.DataDir/"Image"/"mmvLogoWhite.png"
        self.cwd = self.CurrentMaking
        
        # Nuitka command for final export
        nuitka_cmd = NUITKA + [
            "--standalone", "--onefile", "--jobs", "6", 
            "--linux-onefile-icon", icon,
            "--file-reference-choice=runtime",
            # "--nofollow-imports",
            "--follow-imports",
            # "--noinclude-pytest-mode=nofollow",
            # "--noinclude-setuptools-mode=nofollow",
            "--enable-plugin=anti-bloat",
            "--plugin-enable=numpy",
            "--plugin-enable=pkg-resources",

            # Windoe
            "--windows-disable-console",
            "--windows-file-description", "The Interactive Shader Render Platform",
            "--windows-product-version", self.PackageInterface.VersionNumber,
            "--windows-file-version", str(self.PackageInterface.VersionNumber),
            "--windows-product-name", "Modular Music Visualizer",
            "--windows-company-name", "MMV Corp.",
            "--assume-yes-for-downloads",

            # Target file to compile
            str(self.Target)
        ]

        # Make the .bin
        self.SubprocessRun(nuitka_cmd)

        # Remove build directories
        for suffix in [".build", ".dist", ".onefile-build"]:
            self.Rmdir( self.CurrentMaking/(self.TargetBasename+suffix) )

        # Rename the binary to the target final one
        self.CopyRebaseDirToRelease(self.PackageInterface.DataDir)
        self.CopyRebaseDirToRelease(self.PackageInterface.EditorDir/"Nodes")

        if platform == "Linux":
            os.rename(self.CurrentMaking/(self.TargetBasename+".bin"), self.CurrentMaking/"Modular Editor.AppImage")
        elif platform == "Windows":
            os.rename(self.CurrentMaking/(self.TargetBasename+".exe"), self.CurrentMaking/"Modular Editor.exe")

        # Zip
        self.Finish(
            final_zip=self.ReleasesDir/(self.ReleaseName + f" [{platform}].zip"),
            path=self.CurrentMaking,
        )
        self.Clear()

    def CopyRebaseDirToRelease(self, target):
        rebased = str(target).replace( str(self.PackageInterface.DIR), str(self.CurrentMaking) )
        copy_tree(target, rebased)

def main():
    rm = MakeRelease()
    for target in ["Linux", "Windows", "MacOS"]:
        if target in sys.argv: rm.Make(target)

if __name__ == "__main__":
    main()
