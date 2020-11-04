"""
===============================================================================

Purpose: Produce a complete Windows release for the MMV project

Never spend 5 minutes doing something by hand when you can fail
automating it in 5 hours

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

from distutils.dir_util import copy_tree
import subprocess
import shutil
import os


class MakeRelease:
    def __init__(self, mmv, **kwargs):
        self.mmv = mmv

        debug_prefix = "[MakeRelase.__init__]"

        # Can't make release for Windows under Windows
        if self.mmv.utils.os in ["windows", "darwin"]:
            print(debug_prefix, f"Making releases on OS [{self.mmv.utils.os}] not supported, only [linux]")

        # The OS environment vars, we'll change WINEPREFIX and WINEDEBUG on it
        self.env = os.environ.copy()

        # Where this file is located
        self.THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Where we'll use wine
        self.wineprefix = self.THIS_FILE_DIR + "/wineprefix"
        print(debug_prefix, f"WINEPREFIX is [{self.wineprefix}]")

        # Change env WINEPREFIX
        self.change_env("WINEPREFIX", self.wineprefix)

        # No debug information, clean outputs
        self.change_env("WINEDEBUG", "-all")

        # Target release directory
        self.release_dir = f"{self.THIS_FILE_DIR}/release/{self.mmv.misc.version}"
        self.mmv.utils.rmdir(self.release_dir)
        self.mmv.utils.rmdir(self.THIS_FILE_DIR + "/../build")

    # Change a key on copied environment
    def change_env(self, key, value):
        print(f"[MakeRelase.change_env] Changing {key}={value}")
        self.env[key] = value

    # Add directory to this path
    def add_to_env_path(self, add):
        print(f"[MakeRelease.add_to_env_path] Add path to env PATH: [{add}]")
        self.env["PATH"] = f"{add}:" + self.env["PATH"]

    # Print command list on screen and call subprocess
    def display_run_command(self, command):
        print("[MakeRelease.display_run_command] Running command:", command)
        subprocess.check_call(command, env = self.env)

    # Create zipped release
    def create(self):

        # # Check if we have wine and winetricks installed

        if not self.mmv.utils.has_executable_with_name("wine"):
            raise RuntimeError("Please have wine package installed on your Linux distro")

        if not self.mmv.utils.has_executable_with_name("winetricks"):
            raise RuntimeError("Please have winetricks package installed on your Linux distro")

        # # Steps to make an release

        self.create_wineprefix()
        # self.install_wine_python_quiet()
        self.wine_python_upgrade_pip_install_wheel()
        self.install_wine_python_dependencies()
        self.generate_binary_with_pyinstaller()

        # Move build files
        self.mmv.utils.move(self.THIS_FILE_DIR + "/../build/exe.win-amd64-3.8/", self.release_dir)

        # Create dirs
        self.mmv.utils.mkdir_dne(self.release_dir + "/mmv/externals")
        self.mmv.utils.mkdir_dne(self.release_dir + "/mmv/data")
        self.mmv.utils.mkdir_dne(self.release_dir + "/assets")

        # Move FFmpeg
        self.mmv.utils.copy(self.mmv.context.externals + "/ffmpeg.exe", self.release_dir + "/ffmpeg.exe")

        # Move free assets folder
        copy_tree(self.THIS_FILE_DIR + "/../assets/free_assets", self.release_dir + "/assets/free_assets")
        copy_tree(self.THIS_FILE_DIR + "/data", self.release_dir + "/mmv/data")

        self.mmv.utils.copy(
            self.wineprefix + "/drive_c/Program Files/Python38/python38.dll",
            self.release_dir + "/python38.dll"
        )

        self.mmv.utils.mkdir_dne(self.release_dir + "/lib/_soundfile_data")


    # Call wineboot on wineprefix
    def create_wineprefix(self):
        self.display_run_command(["wine", "wineboot"])

    # Download Python to externals dir, installs unnatended
    def install_wine_python_quiet(self):
        debug_prefix = "[MakeRelase.install_python_quiet]"

        # Download Python to externals directory
        save_python = self.mmv.context.externals + "/python-3.8.3-amd64.exe"
        self.mmv.download.wget("https://www.python.org/ftp/python/3.8.3/python-3.8.3-amd64.exe", save_python)

        # Install unnatended
        print(debug_prefix, "Installing Python quiet and unnatended")
        self.display_run_command(["wine", save_python, "/quiet", "InstallAllUsers=1", "PrependPath=1"])

    # Installs wheel and upgrades pip
    def wine_python_upgrade_pip_install_wheel(self):
        debug_prefix = "[MakeRelase.wine_python_upgrade_pip_install_wheel]"

        # Upgrade pip
        print(debug_prefix, "Upgrading pip")
        self.display_run_command(["wine", "python", "-m", "pip", "install", "--upgrade", "pip"])

        # Install wheel
        print(debug_prefix, "Installing wheel package")
        self.display_run_command(["wine", "python", "-m", "pip", "install", "wheel"])
    
    # Install requirements.txt, pyinstaller and extra deps
    def install_wine_python_dependencies(self):
        debug_prefix = "[MakeRelase.install_wine_python_dependencies]"

        # Install requirements.txt
        print(debug_prefix, "Installing MMV requirements.txt dependencies")
        self.display_run_command(["wine", "python", "-m", "pip", "install", "-r", self.THIS_FILE_DIR + "/requirements.txt"])

        # Pyinstaller
        print(debug_prefix, "Installing pyinstaller and deps")
        self.display_run_command(["wine", "python", "-m", "pip", "install", "pyinstaller", "pypiwin32", "pywin32", "py2exe", "cx_freeze"])

        print(debug_prefix, "Installing vcrun2015 with winetricks")
        self.display_run_command(["winetricks", "--unattended", "vcrun2015"])

    def generate_binary_with_pyinstaller(self):
        debug_prefix = "[MakeRelase.generate_binary_with_pyinstaller_onefile]"

        # Add paths to env if required
        self.add_to_env_path(self.THIS_FILE_DIR)
        self.add_to_env_path(self.THIS_FILE_DIR + "/../")

        # I had to remove this file for pyinstaller to work...
        weirdo_file = self.wineprefix + "/drive_c/Program Files/Python38/Lib/site-packages/_soundfile_data/COPYING"
        print(debug_prefix, f"Removing file [{weirdo_file}]")

        try:
            os.remove(weirdo_file)
        except FileNotFoundError:
            print(debug_prefix, f"Couldn't remove the file, already deleted?")

        # self.display_run_command(["wine", "pyinstaller", self.THIS_FILE_DIR + "/../example_basic.py", "--hidden-import=_cffi_backend", "--exclude-module=tkinter"])
        # self.display_run_command(["wine", "build_exe", self.THIS_FILE_DIR + "/../example_basic.py", "-c", "--bundle-files", "0", "-p", "mmv"])
        self.display_run_command(["wine", "python", self.THIS_FILE_DIR + "/../setup.py", "build"])


    # def download_move_glfw_shared_lib(self):
    #     version = "3.3.2"
    #     zipped = "glfw-3.3.2.bin.WIN64"

    #     self.mmv.download.wget(
    #         f"https://github.com/glfw/glfw/releases/download/{version}/{zipped}.zip",
    #         self.mmv.context.externals + "/glfw.zip"
    #     )

    #     self.mmv.download.extract_zip(
    #         self.mmv.context.externals + "/glfw.zip",
    #         self.mmv.context.externals
    #     )

    #     self.mmv.utils.move(
    #         self.mmv.context.externals + f"/{zipped}/lib-vc2019/glfw3.dll",
    #         self.release_dir
    #     )