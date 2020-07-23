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

from mmv.common.interpolation import Interpolation
from mmv.mmv_visualizer import MMVVisualizer
from mmv.common.utils import Utils
from mmv.mmv_image import MMVImage
from mmv.mmv_modifiers import *
import random
import copy
import math
import os


class MMVParticleGenerator():
    def __init__(self, context):
        self.context = context
        self.utils = Utils()
        self.interpolation = Interpolation()
        self.configure = MMVParticleGeneratorConfigure(self)
        self.type = "mmvgenerator"

        self.is_deletable = False

    # Duck typing, this doesn't do anything
    def blit(self, _):
        pass
    def resolve_pending(self):
        pass

    def next(self, fftinfo, this_step):
        if this_step % 10 == 0:
            return {
                "object": self.get_next(),
                "layer": 3
            }
        return {"object": None}
    

class MMVParticleGeneratorConfigure:
    def __init__(self, mmvgenerator):
        self.mmvgenerator = mmvgenerator
        self.generate = MMVParticleGeneratorGenerate(self.mmvgenerator)
    
    def preset_bottom_mid_top(self):
        self.mmvgenerator.get_next = self.generate.preset_bottom_mid_top


class MMVParticleGeneratorGenerate:

    def __init__(self, mmvgenerator):
        self.mmvgenerator = mmvgenerator

    def preset_bottom_mid_top(self):

        particle = MMVImage(self.context)

        particle.image.load_from_path(
            self.utils.random_file_from_dir (
                self.context.assets + os.path.sep + "particles"
            )
        )
        
        horizontal_randomness = 50
        vertical_randomness_min = self.context.height//1.7
        vertical_randomness_max = self.context.height//2.3

        x1 = random.randint(0, self.context.width)
        y1 = self.context.height
        x2 = x1 + random.randint(-horizontal_randomness, horizontal_randomness)
        y2 = y1 + random.randint(-vertical_randomness_min, -vertical_randomness_max)
        x3 = x2 + random.randint(-horizontal_randomness, horizontal_randomness)
        y3 = y2 + random.randint(-vertical_randomness_min, -vertical_randomness_max)

        particle_shake = Shake({
            "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
            "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
            "x_steps": "end_interpolation",
            "y_steps": "end_interpolation",
            "distance": 18,
            "arg_a": 0.01,
            "arg_b": 0.04,
        })

        fast = 0.05
        fade_intensity = random.uniform(0.1, 0.7)

        this_steps = random.randint(50, 100)
        particle.path[0] = {
            "position": [
                Line(
                    (x1, y1),
                    (x2, y2),
                ),
                particle_shake
            ],
            "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
            "interpolation_x_arg_a": fast,
            "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
            "interpolation_y_arg_a": fast,
            "steps": this_steps,
            "modules": {
                "fade": {
                    "interpolation": copy.deepcopy(self.interpolation.linear),
                    "arg_a": None,
                    "object": Fade(
                        start_percentage=0,
                        end_percentage=fade_intensity,
                        finish_steps=50,
                    )
                }
            }
            
        }
        this_steps = random.randint(150, 200)
        particle.path[1] = {
            "position": [
                Line(
                    (x2, y2),
                    (x3, y3),
                ),
                particle_shake
            ],
            "interpolation_x": copy.deepcopy(self.interpolation.remaining_approach),
            "interpolation_x_arg_a": fast,
            "interpolation_y": copy.deepcopy(self.interpolation.remaining_approach),
            "interpolation_y_arg_a": fast,
            "steps": this_steps,
            "modules": {
                "fade": {
                    "interpolation": copy.deepcopy(self.interpolation.linear),
                    "arg_a": None,
                    "object": Fade(
                        start_percentage=fade_intensity,
                        end_percentage=0,
                        finish_steps=this_steps,
                    )
                }
            }
        }

        particle.image.resize_by_ratio(
            random.uniform(0.1, 0.3),
            override=True
        )

        return particle

