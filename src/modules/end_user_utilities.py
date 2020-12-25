"""
===============================================================================

Purpose: Check requirements.txt dependencies, downloads required ones if any

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

import subprocess
import pip
import sys
import os

class Requirements:
    def __init__(self) -> None:
        debug_prefix = "[Requirements.__init__]"

        # Can't run on Python 32 bits
        if not self.is_64_bit():
            print(debug_prefix, "[ERROR] Python installation is not 64 bits, [skia-python] package doesn't support 32 bit installations, please uninstall Python and install a 64 bit version of it.")
            sys.exit(-1)
        else:
            print(debug_prefix, "Python installation is 64 bits OK")

        # This is an release binary, we don't need to install anything
        if getattr(sys, 'frozen', False):
            self.need_to_run = False
            print(debug_prefix, "No need to run Requirements, is a executable binary")
            return
        else:
            print(debug_prefix, "Need to run Requirements, running from source")
            self.need_to_run = True

        self.THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.sep = os.path.sep

        # Requirements
        self.requirements = []
        self.requirements_file = f"{self.THIS_FILE_DIR}/../mmv{self.sep}requirements.txt"

        # Open requirements.txt file
        with open(self.requirements_file, "r") as requirements_file:

            # Each line is a dependency
            for line in requirements_file:

                # If not EOF (hopefully)
                if not line == "\n":
                    self.requirements.append(line.replace("\n", ""))
        
    # Is this python installation 64 bits?
    def is_64_bit(self) -> bool:
        return sys.maxsize > 2**32
        
    # Get a list of installed packages
    def get_installed_packages(self) -> None:
        self.installed = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode("utf-8").replace("\r", "").split("\n")

    # Upgrade pip installation
    def upgrade_pip(self):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])

    # Install an pip package
    def _install(self, package) -> None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    # Is there anything to do?
    def anything_to_do(self) -> bool:
        debug_prefix = "[Requirements.anything_to_do]"

        for requirement in self.requirements:
            if not requirement in self.installed:
                print("[Requirements.anything_to_do] Have requirements to install")
                
                # # Upgrade pip and install wheel, can cause less troubles on installing other deps
                print(debug_prefix, "Upgrading PIP if needed")
                self.upgrade_pip()

                print(debug_prefix, "Installing [wheel] package, less trouble installing other ones")
                self._install("wheel")
                
                return True
        return False

    # Checks, install all dependencies
    def install(self) -> None:
        debug_prefix = "[Requirements.install]"
        MODE = "automatic"

        self.get_installed_packages()

        # Do we have any dependency to install?
        if self.anything_to_do():

            # Call pip install -r requirements.txt
            if MODE == "automatic":
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', "wheel"])
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', self.requirements_file])

            # Install packages on a loop
            elif MODE == "manual":
                self.get_installed_packages()

                print(debug_prefix, "Requirements =", self.requirements)
                print(debug_prefix, "Installed =", self.installed)

                # For each requirement
                for requirement in self.requirements:

                    # Requirement is installed
                    if requirement in self.installed:
                        print(debug_prefix, f"Requirement [{requirement}] OK")

                    # Requirement is not installed
                    else:
                        print(debug_prefix, f"Requirement [{requirement}] NO")
                        self._install(requirement)
                        self.get_installed_packages()
        else:
            print(debug_prefix, "Nothing to do, all requirements matched")
                
class ArgParser:
    def __init__(self, argv):
        self.argv = argv
        self.parse_argv()
        
    # Check for flags on argv
    def parse_argv(self):
        debug_prefix = "[ArgParser]"

        # Empty list of flags and kflags
        self.flags = []
        self.kflags = {}

        if self.argv is not None:

            # Iterate in all args
            for arg in self.argv[1:]:
                
                # Is a kwarg
                if "=" in arg:
                    arg = arg.split("=")
                    self.kflags[arg[0]] = arg[1]

                # Is a flag
                else:
                    self.flags.append(arg)
        
        self.auto_deps = "--auto-deps" in self.flags
        print(debug_prefix, "--auto-deps True") if self.auto_deps else print(debug_prefix, "--auto-deps False")

        if "render" in self.kflags.keys():
            render = self.kflags["render"]
            
            # Only two modes available
            assert render in ["gpu", "cpu"]

            print(debug_prefix, f"Render target is [{render}]")
            self.render = render
        else:
            print(debug_prefix, "No given render target flag, assuming [gpu]")
            self.render = "gpu"
        