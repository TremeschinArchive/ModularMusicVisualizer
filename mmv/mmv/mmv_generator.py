"""
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


class MMVGenerator:
    def __init__(self, mmv) -> None:
        self.mmv = mmv
        self.generator = None

    def next(self) -> dict:
        return self.generator.next()

    # Set a particle generator object
    def particle_generator(self, **kwargs) -> None:
        self.generator = MMVParticleGenerator(self.mmv, **kwargs)

