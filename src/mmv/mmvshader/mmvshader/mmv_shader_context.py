"""
===============================================================================

Purpose: Configurations, runtime variables for MMV

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

import os


# Manage directories
class Directories:
    def __init__(self, main):
        debug_prefix = "[Directories.__init__]"
        self.mmv_main = main

        # Generate and create required directories

        # Generated shaders from template
        self.runtime = f"{self.mmv_main.DIR}{os.path.sep}runtime"
        print(debug_prefix, f"Runtime directory is [{self.runtime}]")
        self.mmv_main.utils.rmdir(self.runtime)
        self.mmv_main.utils.mkdir_dne(self.runtime)

# Free real state for changing, modifying runtime dependent vars
class Runtime:
    def __init__(self, main):
        debug_prefix = "[Runtime.__init__]"
        self.mmv_main = main


# Context vars (configured stuff)
class Context:
    def __init__(self, main):
        debug_prefix = "[Context.__init__]"
        self.mmv_main = main

        print(debug_prefix, "Creating Directories")
        self.directories = Directories(self.mmv_main)

        print(debug_prefix, "Creating Runtime")
        self.runtime = Runtime(self.mmv_main)
