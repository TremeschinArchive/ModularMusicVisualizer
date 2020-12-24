"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMV objects generators

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

from mmv.generators.mmv_particle_generator import MMVParticleGenerator
from mmv.common.cmn_constants import LOG_NEXT_DEPTH, ROOT_DEPTH, LOG_NO_DEPTH
import logging


class MMVGenerator:
    def __init__(self, mmv_main, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVGenerator.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_main = mmv_main

        # Log the creation of this class
        logging.info(f"{depth}{debug_prefix} Created new MMVGenerator object, getting unique identifier for it")

        # Get an unique identifier for this MMVImage object
        self.identifier = self.mmv_main.utils.get_unique_id(
            purpose = "MMVImage object", depth = ndepth
        )

        logging.info(f"{depth}{debug_prefix} [{self.identifier}] Starting with empty generator attribute")
        self.generator = None

    # Main routine, wraps around generator files under the "generators" directory
    def next(self) -> dict:
        return self.generator.next()

    # Set a particle generator object
    def particle_generator(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVGenerator.particle_generator]"
        ndepth = depth + LOG_NEXT_DEPTH

        logging.info(f"{depth}{debug_prefix} [{self.identifier}] Setting this generator object to MMVParticleGenerator with kwargs: {kwargs}")

        self.generator = MMVParticleGenerator(self.mmv_main, **kwargs)

