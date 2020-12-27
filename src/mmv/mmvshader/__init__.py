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
from mmv.common.cmn_tree import DisplayablePath
from pathlib import Path
import logging
import toml
import sys
import os


# Main wrapper class for the end user, facilitates MMV in a whole
class MMVShaderInterface:

    # This top level interface is the "global package manager" for every subproject / subimplementation of
    # MMV, it is the class that will deal with stuff not directly related to functionality of this class 
    # and package here, mainly dealing with external deps, micro managing stuff, setting up logging,
    # loading "prelude" configurations, that is, defining behavior, not configs related to this package
    # and functionality.
    #
    # We create a MMV{Skia,Shader}Main class and we send this interface to it, and we send that instance
    # of MMV*Main to every other sub class so if we access self.mmv_main.interface we are accessing this
    # file here, MMVShaderInterface, and we can quickly refer to the most top level package by doing
    # self.mmv_main.interface.top_level_interface, since this interface here is just the MMVSkia 
    # interface for the mmvshader package while the top level one manages both MMVSkia and MMVShader
    #
    def __init__(self, top_level_interace, depth = LOG_NO_DEPTH, **kwargs):
        debug_prefix = "[MMVShaderInterface.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.top_level_interace = top_level_interace
        self.os = self.top_level_interace.os
  
        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_main.interface.MMV_SHADER_ROOT at any depth in the code
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

        # # Where stuff will be located

        self.SHADERS_LOCATED_AT = f"{self.MMV_SHADER_ROOT}{os.path.sep}glsl"
        logging.info(f"{depth}{debug_prefix} Shader folder / files should be located at [{self.SHADERS_LOCATED_AT}]")

        logging.info(LOG_SEPARATOR)

    # List the shaders on the self.SHADERS_LOCATED_AT folder and also
    # reads every shader for pattern matching and printing available
    # options / settings
    def list_shaders(self, depth = LOG_NEXT_DEPTH):
        debug_prefix = "[list_shaders]"
        logging.info(f"{depth}{debug_prefix} Listing shader paths and documentation")
        logging.info(STEP_SEPARATOR)
        depth = depth + LOG_NEXT_DEPTH

        # # Read every file and print documentation (lines starting with ///)
        for root, d, f in os.walk(self.SHADERS_LOCATED_AT):
            for file in f:
                file = os.path.join(root, file)
                if file.endswith(".glsl"):
                    logging.info(f"{depth}{debug_prefix} File: [{file}]")
                    with open(file, "r") as glsl:
                        for line in glsl:
                            if line.startswith("//DESC"):
                                line = line.replace("//DESC", "").replace("//DESC ", "").replace("\n", "")
                                logging.info(f"{depth}{debug_prefix} >{line}")
                    logging.info(STEP_SEPARATOR)

        # # Pretty printing the whole directory

        logging.info(f"{depth}{debug_prefix} [Here's the complete file / folder tree structure of the GLSL shaders directory]:")

        # Create a iterator for printing the tree of the directory
        paths = DisplayablePath.make_tree(Path(self.SHADERS_LOCATED_AT))
        
        # Print every path
        for path in paths:
            logging.info(f"{depth}{debug_prefix} :: {path.displayable()}")

