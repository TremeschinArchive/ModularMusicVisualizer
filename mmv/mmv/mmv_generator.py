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

from mmv.mmv_classes import *
from mmv.mmv_generators.mmv_particle_generator import MMVParticleGenerator
from mmv.common.interpolation import Interpolation
from mmv.mmv_visualizer import MMVVisualizer
from mmv.common.utils import Utils
from mmv.mmv_image import MMVImage
from mmv.mmv_modifiers import *
import random
import copy
import math
import os


class MMVGenerator:
    def __init__(self, context: Context) -> None:
        self.context = context
        self.generator = None

    def next(self, fftinfo: dict, this_step: int) -> dict:
        return self.generator.next(fftinfo, this_step)

    def particle_generator(self) -> None:
        self.generator = MMVParticleGenerator(self.context)
        
