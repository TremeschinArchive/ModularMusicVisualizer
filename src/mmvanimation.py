"""
===============================================================================

Purpose: MMVAnimation object

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

from mmvimage import MMVImage
from modifiers import *
from utils import Utils
import random
import math
import os


class MMVAnimation():
    def __init__(self, context, controller, canvas, audio):
        self.context = context
        self.controller = controller
        self.canvas = canvas
        self.audio = audio

        self.utils = Utils()

        self.content = {}

        n_layers = 10
        for n in range(n_layers):
            self.content[n] = []

    # Call every next step of the content animations
    def next(self, audio_slice, fft):

        # Calculate some fft from the audio
        biased_total_size = abs(sum(fft)) / self.context.batch_size
        average_value = sum([abs(x)/(2**self.audio.info["bit_depth"]) for x in audio_slice]) / len(audio_slice)

        fftinfo = {
            "average_value": average_value,
            "biased_total_size": biased_total_size,
        }

        # print(">>>>", fftinfo, audio_slice)

        for zindex in sorted(list(self.content.keys())):
            for item in self.content[zindex]:
                if item.is_deletable:
                    del item
                    continue

                # Generate next step of animation
                item.next(fftinfo)

                # Blit itself on the canvas
                item.blit(self.canvas)
        
        self.add_random_particle()
    
    def add_random_particle(self):
        temp = MMVImage(self.context)
        temp.image.load_from_path(
            self.utils.random_file_from_dir (
                self.context.assets + os.path.sep + "particles"
            )
        )
        temp.image.resize_by_ratio( random.uniform(0.05, 0.1) )
        x1 = random.randint(0, 1280)
        y1 = random.randint(0, 720)
        x2 = x1 + random.randint(-50, 50)
        y2 = y1 + random.randint(-50, 50)
        x3 = x2 + random.randint(-50, 50)
        y3 = y2 + random.randint(-50, 50)

        # temp.path[0] = {
        #     "position": Point(x1, y1),
        #     "interpolation_x": "linear",
        #     "interpolation_y": "linear",
        #     "steps": 1,
        # }
        # temp.path[1] = {
        #     "position": Line(
        #         (x1, y1),
        #         (x2, y2),
        #     ),
        #     "interpolation_x": "linear",
        #     "interpolation_y": "sigmoid",
        #     "interpolation_y_arg_a": 10,
        #     "steps": random.randint(50, 100)
        # }
        # temp.path[2] = {
        #     "position": Line(
        #         (x2, y2),
        #         (x3, y3),
        #     ),
        #     "interpolation_x": "sigmoid",
        #     "interpolation_x_arg_a": 10,
        #     "interpolation_y": "linear",
        #     "steps": random.randint(150, 200)
        # }

        fast = 0.05

 
        temp.path[0] = {
            "position": Line(
                (x1, y1),
                (x2, y2),
            ),
            "interpolation_x": "remaining_approach",
            "interpolation_x_arg_a": fast,
            "interpolation_y": "remaining_approach",
            "interpolation_y_arg_a": fast,
            "steps": random.randint(50, 100)
        }
        temp.path[1] = {
            "position": Line(
                (x2, y2),
                (x3, y3),
            ),
            "interpolation_x": "remaining_approach",
            "interpolation_x_arg_a": fast,
            "interpolation_y": "remaining_approach",
            "interpolation_y_arg_a": fast,
            "steps": random.randint(150, 200)
        }

        self.content[1].append(temp)

    def add_background(self):
        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": Point(0, 0),
            "steps": math.inf,
            "interpolation_x": None,
            "interpolation_y": None,
            "testlink": None,
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "background" + os.path.sep + "ten.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width,
            self.context.height,
            override=True
        )

        self.content[0] = [temp]

    # Generate the objects on the animation
    # TODO: PROFILES, CURRENTLY MANUALLY SET HERE
    def generate(self):
        self.add_background()

        