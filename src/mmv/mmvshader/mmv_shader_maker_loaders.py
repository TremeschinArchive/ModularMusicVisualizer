"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Load stuff from config files

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
from mmv.mmvshader.abstractions.abstraction_block_of_code import BlockOfCode
from mmv.common.cmn_utils import Utils
import logging


class MMVShaderMakerLoaders:
    def __init__(self, mmv_shader_maker):
        
        # Get master class
        self.mmv_shader_maker = mmv_shader_maker
        self.transformations = self.mmv_shader_maker.transformations

        self.utils = Utils()
        
    def from_yaml(self, path):
        debug_prefix = "[MMVShaderMakerLoaders.from_yaml]"

        logging.info(f"{debug_prefix} Loading config from YAML file [{path}]")
        data = self.utils.load_yaml(path)
    