"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, PACKAGE_DEPTH, LOG_NO_DEPTH, LOG_SEPARATOR, STEP_SEPARATOR
from mmv.mmvshader.mmv_shader_main import MMVShaderMain
import logging
import toml
import sys
import os


# Main wrapper class for the end user, facilitates MMV in a whole
class MMVShaderInterface:

    def __init__(self, top_level_interace, depth = LOG_NO_DEPTH, **kwargs):
        debug_prefix = "[MMVShaderInterface.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.top_level_interace = top_level_interace
        self.os = self.top_level_interace.os
  
        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_main.MMV_SHADER_ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.MMV_SHADER_ROOT = os.path.dirname(os.path.abspath(__file__))
            logging.info(f"{depth}{debug_prefix} Running directly from source code")
            logging.info(f"{depth}{debug_prefix} Modular Music Visualizer Python package [__init__.py] located at [{self.MMV_SHADER_ROOT}]")
        else:
            self.MMV_SHADER_ROOT = os.path.dirname(os.path.abspath(sys.executable))
            logging.info(f"{depth}{debug_prefix} Running from release (sys.executable..?)")
            logging.info(f"{depth}{debug_prefix} Modular Music Visualizer executable located at [{self.MMV_SHADER_ROOT}]")

        # # Prelude configuration

        prelude_file = f"{self.MMV_SHADER_ROOT}{os.path.sep}mmv_shader_prelude.toml"
        logging.info(f"{depth}{debug_prefix} Attempting to load prelude file located at [{prelude_file}], we cannot continue if this is wrong..")

        with open(prelude_file, "r") as f:
            self.prelude = toml.loads(f.read())

        # Log prelude configuration
        logging.info(f"{depth}{debug_prefix} Prelude configuration is: {self.prelude}")

        # # # Create MMV classes and stuff

        logging.info(f"{depth}{debug_prefix} Creating MMVShaderMain")
        self.mmv_shader_main = MMVShaderMain(interface = self, depth = ndepth)

        logging.info(LOG_SEPARATOR)
