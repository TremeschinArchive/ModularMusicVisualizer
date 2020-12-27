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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
import logging
import os


# Manage directories
class MMVShaderDirectories:
    def __init__(self, mmv_shader_main, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderDirectories.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_shader_main = mmv_shader_main

        # Generate and create required directories

        # Generated shaders from template
        self.runtime = f"{self.mmv_shader_main.MMV_SHADER_ROOT}{os.path.sep}runtime{os.path.sep}mmvshader_runtime_glsl"

        logging.info(f"{depth}{debug_prefix} MMVShader Runtime directory is [{self.runtime}]")
        
        self.mmv_shader_main.utils.rmdir(path = self.runtime, depth = ndepth)
        self.mmv_shader_main.utils.mkdir_dne(path = self.runtime, depth = ndepth)


# Free real state for changing, modifying runtime dependent vars
class MMVShaderRuntime:
    def __init__(self, mmv_shader_main, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderRuntime.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_shader_main = mmv_shader_main


# MMVShaderContext vars (configured stuff)
class MMVShaderContext:
    def __init__(self, mmv_shader_main, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderContext.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_shader_main = mmv_shader_main

        logging.info(f"{depth}{debug_prefix} Creating MMVShaderDirectories")
        self.directories = MMVShaderDirectories(mmv_shader_main = self.mmv_shader_main, depth = ndepth)

        logging.info(f"{depth}{debug_prefix} Creating MMVShaderRuntime")
        self.runtime = MMVShaderRuntime(mmv_shader_main = self.mmv_shader_main, depth = ndepth)
