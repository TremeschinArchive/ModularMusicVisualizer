"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

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
class MMVShaderDirectories:
    def __init__(self, main):
        debug_prefix = "[MMVShaderDirectories.__init__]"
        self.mmv_shader_main = main

        # Generate and create required directories

        # Generated shaders from template
        self.runtime = f"{self.mmv_shader_main.MMV_SHADER_ROOT}{os.path.sep}runtime"
        print(debug_prefix, f"MMVShaderRuntime directory is [{self.runtime}]")
        self.mmv_shader_main.utils.rmdir(self.runtime)
        self.mmv_shader_main.utils.mkdir_dne(self.runtime)


# Free real state for changing, modifying runtime dependent vars
class MMVShaderRuntime:
    def __init__(self, main):
        debug_prefix = "[MMVShaderRuntime.__init__]"
        self.mmv_shader_main = main


# MMVShaderContext vars (configured stuff)
class MMVShaderContext:
    def __init__(self, main):
        debug_prefix = "[MMVShaderContext.__init__]"
        self.mmv_shader_main = main

        print(debug_prefix, "Creating MMVShaderDirectories")
        self.directories = MMVShaderDirectories(self.mmv_shader_main)

        print(debug_prefix, "Creating MMVShaderRuntime")
        self.runtime = MMVShaderRuntime(self.mmv_shader_main)
