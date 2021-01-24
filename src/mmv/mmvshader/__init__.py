"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Interface for MMVShader functionality

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

from mmv.mmvshader.mmv_shader_mgl import MMVShaderMGL
from mmv.common.cmn_constants import STEP_SEPARATOR
import logging
import toml
import sys
import os


# Main wrapper class for the end user, facilitates MMV in a whole
class MMVShaderInterface:

    def get_mgl_interface(self):
        return MMVShaderMGL()

    def __init__(self, top_level_interace, **kwargs):
        debug_prefix = "[MMVShaderInterface.__init__]"

        self.top_level_interace = top_level_interace
  
        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_skia_main.interface.MMV_SHADER_ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.MMV_SHADER_ROOT = os.path.dirname(os.path.abspath(__file__))
            logging.info(f"{debug_prefix} Running directly from source code")
            logging.info(f"{debug_prefix} Modular Music Visualizer Python package [__init__.py] located at [{self.MMV_SHADER_ROOT}]")
        else:
            self.MMV_SHADER_ROOT = os.path.dirname(os.path.abspath(sys.executable))
            logging.info(f"{debug_prefix} Running from release (sys.executable..?)")
            logging.info(f"{debug_prefix} Modular Music Visualizer executable located at [{self.MMV_SHADER_ROOT}]")

        # Free real state runtime dir for temp files
        self.runtime_dir = f"{self.MMV_SHADER_ROOT}{os.path.sep}runtime"
