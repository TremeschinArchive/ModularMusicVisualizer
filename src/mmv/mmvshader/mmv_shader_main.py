"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Utility to wrap around mpv and add processing shaders, target
resolutions, input / output

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH, STEP_SEPARATOR
from mmv.mmvshader.mmv_shader_context import MMVShaderContext
from mmv.mmvshader.mmv_shader_maker import MMVShaderMaker
from mmv.mmvshader.mmv_shader_mpv import MMVShaderMPV
from mmv.common.cmn_utils import Utils
import logging
import shutil
import math
import sys
import os


class MMVShaderMain:
    def __init__(self, interface, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVShaderMain.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.interface = interface

        self.MMV_SHADER_ROOT = self.interface.MMV_SHADER_ROOT
        self.prelude = self.interface.prelude
        self.os = self.interface.os

        # # Create classes

        logging.info(f"{depth}{debug_prefix} Creating Utils")
        logging.info(STEP_SEPARATOR)
        self.utils = Utils()

        logging.info(f"{depth}{debug_prefix} Creating MMVShaderContext")
        logging.info(STEP_SEPARATOR)
        self.context = MMVShaderContext(self)

        logging.info(f"{depth}{debug_prefix} Creating MMVShaderMPV")
        logging.info(STEP_SEPARATOR)
        self.mpv = MMVShaderMPV(self)

        logging.info(f"{depth}{debug_prefix} Creating MMVShaderMaker")
        logging.info(STEP_SEPARATOR)
        self.shader_maker = MMVShaderMaker(self)

