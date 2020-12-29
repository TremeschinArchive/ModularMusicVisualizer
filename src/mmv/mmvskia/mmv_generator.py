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

from mmv.mmvskia.generators.mmv_particle_generator import MMVSkiaParticleGenerator
from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
import logging


class MMVSkiaGenerator:
    def __init__(self, mmvskia_main, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaGenerator.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmvskia_main = mmvskia_main
        self.preludec = self.mmvskia_main.mmvskia_interface.prelude["mmvgenerator"]
 
        # Get an unique identifier for this MMVSkiaImage object
        self.identifier = self.mmvskia_main.utils.get_unique_id(
            purpose = "MMVSkiaImage object", depth = ndepth,
            silent = self.preludec["log_get_unique_id"]
        )

        # Log the creation of this class
        if self.preludec["log_creation"]:
            logging.info(f"{depth}{debug_prefix} [{self.identifier}] Created new MMVSkiaGenerator object, getting unique identifier for it")

        # Start with empty generator object
        self.generator = None

    # Main routine, wraps around generator files under the "generators" directory
    def next(self) -> dict:
        return self.generator.next()

    # Set a particle generator object
    def particle_generator(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaGenerator.particle_generator]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["particle_generator"]:
            logging.info(f"{depth}{debug_prefix} [{self.identifier}] Setting this generator object to MMVSkiaParticleGenerator with kwargs: {kwargs}")

        # Set this generator to a MMVSkiaParticleGenerator
        self.generator = MMVSkiaParticleGenerator(self.mmvskia_main, depth = ndepth, **kwargs)
