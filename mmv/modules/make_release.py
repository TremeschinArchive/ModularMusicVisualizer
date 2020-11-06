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
        self.project_root = kwargs["project_root"]
        self.mmv_folder = kwargs["mmv_folder"]

        # Target release directory
        self.release_dir = f"{self.project_root}/release"
        self.final_release_dir = f"{self.release_dir}/{self.mmv.misc.version}"

        # Reset previous builds
        self.mmv.utils.rmdir(self.project_root + "/build")
        self.mmv.utils.rmdir(self.project_root + "/dist")

        # Where we'll use wine
        self.wineprefix = self.mmv.utils.get_abspath("~/.mmv")
        print(debug_prefix, f"WINEPREFIX is [{self.wineprefix}]")

        # Change env WINEPREFIX
        self.change_env("WINEPREFIX", self.wineprefix)

        # No debug information, clean outputs
        self.change_env("WINEDEBUG", "-all")

        self.RELEASE_MAKER = kwargs.get("release_maker", "pyinstaller")
        self.ONEFILE = kwargs.get("onefile", True)
       
        # Windows Python version to download and use
        self.PYTHON_VERSION_FULL = kwargs.get("python", ["3.7.9", "3.8.6"][1])

        self.PYTHON_VERSION_MAJOR = ".".join(self.PYTHON_VERSION_FULL.split(".")[0:2])
        self.PYTHON_VERSION_MAJOR_NO_DOT = self.PYTHON_VERSION_MAJOR.replace(".", "")

        print(debug_prefix, f"Python version full         = [{self.PYTHON_VERSION_FULL}]")
        print(debug_prefix, f"Python version major        = [{self.PYTHON_VERSION_MAJOR}]")
        print(debug_prefix, f"Python version major no dot = [{self.PYTHON_VERSION_MAJOR_NO_DOT}]")

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
        subprocess.check_call(command, env = self.env, cwd = self.project_root)

    # Create zipped release
    def create(self):

        # # Check if we have wine and winetricks installed

        if not self.mmv.utils.has_executable_with_name("wine"):
            raise RuntimeError("Please have wine package installed on your Linux distro")

        if not self.mmv.utils.has_executable_with_name("winetricks"):
            raise RuntimeError("Please have winetricks package installed on your Linux distro")

        # # Steps to make an release

        self.create_wineprefix()
        self.install_wine_python_quiet()
        self.wine_python_upgrade_pip_install_wheel()
        self.install_wine_python_dependencies()
        self.generate_binary()
        self.move_files()
        self.download_move_glfw_shared_lib()

    # Call wineboot on wineprefix
    def create_wineprefix(self):
        self.display_run_command(["wine", "wineboot"])

    # Download Python to externals dir, installs unnatended
    def install_wine_python_quiet(self):
        debug_prefix = "[MakeRelase.install_python_quiet]"

        # Download Python to externals directory
        save_python = self.mmv.context.externals + f"/python-{self.PYTHON_VERSION_FULL}-amd64.exe"
        get_url = f"https://www.python.org/ftp/python/{self.PYTHON_VERSION_FULL}/python-{self.PYTHON_VERSION_FULL}-amd64.exe"

        print(debug_prefix, f"Downloading Python from URL [{get_url}]")

        self.mmv.download.wget(get_url, save_python)

        # Install unnatended
        print(debug_prefix, "Installing Python quiet and unnatended")

        try:
            self.display_run_command(["wine", save_python, "/quiet", "InstallAllUsers=1", "PrependPath=1"])
        except subprocess.CalledProcessError:
            print(debug_prefix, "[ERROR?] COULDN'T INSTALL PYTHON ON WINEPREFIX, ALREADY INSTALLED OR ERROR?? SAFE TO IGNORE IF ALREADY INSTALLED.")

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
        self.display_run_command(["wine", "python", "-m", "pip", "install", "-r", self.mmv_folder + "/requirements.txt"])

        # Pyinstaller
        # FIXME: Waiting for Wine patch for pyinstaller > 3.6, see https://github.com/pyinstaller/pyinstaller/issues/4628
        print(debug_prefix, "Installing pyinstaller and deps")
        # self.display_run_command(["wine", "python", "-m", "pip", "install", "pyinstaller==3.5", "pypiwin32", "pywin32-ctypes", "pywin32", "py2exe", "cx_freeze"])
        self.display_run_command(["wine", "python", "-m", "pip", "install", "--upgrade", "--force-reinstall", "pyinstaller", "pypiwin32", "pywin32-ctypes", "pywin32", "py2exe", "cx_freeze"])

        print(debug_prefix, "Installing vcrun2015 with winetricks")
        self.display_run_command(["winetricks", "--unattended", "vcrun2015"])

    def generate_binary(self):
        debug_prefix = "[MakeRelase.generate_binary]"

        # Add paths to env if required
        self.add_to_env_path(self.project_root)
        # self.add_to_env_path(self.mmv_folder)
        # self.add_to_env_path(self.THIS_FILE_DIR)

        # I had to remove this file for pyinstaller to work.
        try:
            weirdo_file = self.wineprefix + f"/drive_c/Program Files/Python{self.PYTHON_VERSION_MAJOR_NO_DOT}/Lib/site-packages/_soundfile_data/COPYING"
            print(debug_prefix, f"Removing file [{weirdo_file}]")
            os.remove(weirdo_file)
        except FileNotFoundError:
            print(debug_prefix, f"Couldn't remove the file, already deleted?")
            
        if self.RELEASE_MAKER == "cxfreeze":
            self.display_run_command(["wine", "python", self.project_root + "/setup.py", "build"])

        elif self.RELEASE_MAKER == "pyinstaller":

            # FIXME: HOTFIX
            print(debug_prefix, "[HOTFIX] Upgrading setuptools because pyinstaller")
            self.display_run_command(["wine", "python", "-m", "pip", "install", "--upgrade", "setuptools"])

            # FIXME: cffi shenanigans
            # self.display_run_command(["wine", "python", "-m", "pip", "install", "--upgrade", "--user", "--force-reinstall", "numpy"])
            self.add_to_env_path(self.wineprefix + "/drive_c/Program Files/Python37/DLLs/")
            self.add_to_env_path(self.wineprefix + "/drive_c/Program Files/Python37/libs/")
            self.add_to_env_path(self.wineprefix + "/drive_c/Program Files/Python37/Scripts/")

            # hidden_imports = ["--hidden-import", "mmv", "--hidden-import", "_cffi_backend"]
            # paths = []

            # for root, dirs, files in os.walk(self.mmv_folder):
            #     paths += ["-p", root]
            #     relative = '.'.join(root.replace(self.mmv_folder, "").split(os.path.sep))
            #     for file in files:
            #         if file.endswith(".py"):
            #             file_path = os.path.join(root, file)
            #             paths += ["-p", file_path]
            #             file = file.replace(".py", "")
            #             the_import = f"mmv{relative}.{file}".replace(os.path.sep, ".")
            #             print(debug_prefix, f"Adding [{the_import}] to hidden imports")
            #             hidden_imports += ["--hidden-import", the_import]

            command = [
                "wine", "pyinstaller",
                self.project_root + "/example_basic.py",
                "--exclude-module=tkinter",
                "-p", self.mmv_folder + "/__init__.py", # Paths
                "-p", self.mmv_folder, # Paths
                "--additional-hooks-dir", self.mmv_folder, 
                "--workpath", self.project_root,
                "--clean",
            ]
            # ] + hidden_imports + paths

            if self.ONEFILE:
                command.append("--onefile")

            self.display_run_command(command)
        
        elif self.RELEASE_MAKER == "py2exe":
            self.display_run_command(["wine", "build_exe", self.project_root + "/example_basic.py", "-c", "--bundle-files", "0", "-p", "mmv"])

    def move_files(self):
        debug_prefix = "[MakeRelase.move_files]"

        # Reset final release dir
        self.mmv.utils.rmdir(self.final_release_dir)

        # Make directories
        # self.mmv.utils.mkdir_dne(self.final_release_dir + "/data")
        # self.mmv.utils.mkdir_dne(self.final_release_dir + "/assets")

        if self.RELEASE_MAKER == "cxfreeze":

            # Move build files
            self.mmv.utils.move(self.project_root + f"/build/exe.win-amd64-{self.PYTHON_VERSION_MAJOR}", self.final_release_dir)

            # Rename final MMV binary
            self.mmv.utils.move(self.final_release_dir + "/example_basic.exe", self.final_release_dir + "/mmv.exe")

            # Create dirs
            # self.mmv.utils.mkdir_dne(self.final_release_dir + "/mmv/externals")

            self.mmv.utils.copy(
                self.wineprefix + f"/drive_c/Program Files/Python{self.PYTHON_VERSION_MAJOR_NO_DOT}/python{self.PYTHON_VERSION_MAJOR_NO_DOT}.dll",
                self.final_release_dir + f"/python{self.PYTHON_VERSION_MAJOR_NO_DOT}.dll"
            )
            
        elif self.RELEASE_MAKER == "pyinstaller":
            if self.ONEFILE:
                self.mmv.utils.mkdir_dne(self.final_release_dir)
                self.mmv.utils.move(self.project_root + "/dist/example_basic.exe", self.final_release_dir + "/mmv.exe")
            else:
                copy_tree(self.project_root + "/dist/example_basic", self.final_release_dir)
                # self.mmv.utils.move(self.release_dir + "/example_basic", self.final_release_dir)

        if (self.RELEASE_MAKER == "pyinstaller" and not self.ONEFILE) or self.RELEASE_MAKER == "cxfreeze:":

            # # libsndfile64.dll fix
            target_dir = self.final_release_dir + "/lib/_soundfile_data"

            # self.mmv.utils.mkdir_dne(target_dir)

            self.mmv.download.git_clone(
                "https://github.com/bastibe/libsndfile-binaries",
                self.mmv.context.externals + "/libsndfile-binaries"
            )

            copy_tree(self.mmv.context.externals + "/libsndfile-binaries", target_dir)
            self.mmv.utils.rmdir(target_dir + "/.git")

        # Move FFmpeg
        self.mmv.utils.copy(self.mmv.context.externals + "/ffmpeg.exe", self.final_release_dir + "/ffmpeg.exe")

        # Move free assets folder
        copy_tree(self.project_root + "/assets/free_assets", self.final_release_dir + "/assets/free_assets")
        copy_tree(self.mmv_folder + "/data", self.final_release_dir + "/data")

    def download_move_glfw_shared_lib(self):
        version = "3.3.2"
        zipped = "glfw-3.3.2.bin.WIN64"

        self.mmv.download.wget(
            f"https://github.com/glfw/glfw/releases/download/{version}/{zipped}.zip",
            self.mmv.context.externals + "/glfw.zip"
        )

        self.mmv.download.extract_zip(
            self.mmv.context.externals + "/glfw.zip",
            self.mmv.context.externals
        )

        self.mmv.utils.move(
            self.mmv.context.externals + f"/{zipped}/lib-vc2019/glfw3.dll",
            self.final_release_dir + "/glfw3.dll"
        )