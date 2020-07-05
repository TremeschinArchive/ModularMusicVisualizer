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

from interpolation import Interpolation
from mmvvisualizer import MMVVisualizer
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
        self.interpolation = Interpolation()

        self.content = {}

        n_layers = 10
        for n in range(n_layers):
            self.content[n] = []

    def add_random_particle(self):
        temp = MMVImage(self.context)
        temp.image.load_from_path(
            self.utils.random_file_from_dir (
                self.context.assets + os.path.sep + "particles"
            )
        )
        temp.image.resize_by_ratio( random.uniform(0.05, 0.1) )
        x1 = random.randint(0, 1280)
        # y1 = random.randint(0, 720)
        y1 = 720
        x2 = x1 + random.randint(-50, 50)
        y2 = y1 + random.randint(-400, -300)
        x3 = x2 + random.randint(-50, 50)
        y3 = y2 + random.randint(-400, -300)

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

    def add_moving_background(self):
        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": Point(0, 0),
            "steps": math.inf,
            "interpolation_x": None,
            "interpolation_y": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "1 + 3*x",
                    "arg_a": 0.08,
                },
                "blur": True
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "background.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width,
            self.context.height,
            override=True
        )

        self.content[0] = [temp]

    def add_logo(self):
        logo_size = 200
        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": Point(
                self.context.width // 2 - (logo_size/2),
                self.context.height // 2 - (logo_size/2)
            ),
            "steps": math.inf,
            "interpolation_x": None,
            "interpolation_y": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "1 + 8*x",
                    "arg_a": 0.08,
                }
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "logo" + os.path.sep + "logo.png"
        )
        temp.image.resize_to_resolution(
            logo_size,
            logo_size,
            override=True
        )

        self.content[2] = [temp]

    def add_visualizer(self):
        temp = MMVVisualizer(self.context)
        self.content[0].append(temp)

    # Generate the objects on the animation
    # TODO: PROFILES, CURRENTLY MANUALLY SET HERE
    def generate(self):

        config = {
            "moving_background": False,
            "logo": False,
            "visualizer": True,
        }

        if config["moving_background"]:
            self.add_moving_background()
        
        if config["logo"]:
            self.add_logo()

        if config["visualizer"]:
            self.add_visualizer()

    # Call every next step of the content animations
    def next(self, audio_slice, fft, this_step):

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
        
        if this_step % 5 == 0:
            # print("Adding particle")
            self.add_random_particle()