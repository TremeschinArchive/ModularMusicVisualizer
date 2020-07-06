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
        horizontal_randomness = 50
        vertical_randomness_min = self.context.height//1.7
        vertical_randomness_max = self.context.height//2.3

        x1 = random.randint(0, self.context.width)
        # y1 = random.randint(0, 720)
        y1 = self.context.height
        x2 = x1 + random.randint(-horizontal_randomness, horizontal_randomness)
        y2 = y1 + random.randint(-vertical_randomness_min, -vertical_randomness_max)
        x3 = x2 + random.randint(-horizontal_randomness, horizontal_randomness)
        y3 = y2 + random.randint(-vertical_randomness_min, -vertical_randomness_max)

        particle_shake = Shake({
            "interpolation": self.interpolation.remaining_approach,
            "distance": 18,
            "arg_a": 0.01,
            "arg_b": 0.04,
            "x_steps": "end_interpolation",
            "y_steps": "end_interpolation",
        })

        fast = 0.05
        fade_intensity = random.uniform(0.1, 0.7)

        temp.path[0] = {
            "position": [
                Line(
                    (x1, y1),
                    (x2, y2),
                ),
                particle_shake
            ],
            "interpolation_x": self.interpolation.remaining_approach,
            "interpolation_x_arg_a": fast,
            "interpolation_y": self.interpolation.remaining_approach,
            "interpolation_y_arg_a": fast,
            "steps": random.randint(50, 100),
            "modules": {
                "fade": {
                    "interpolation": self.interpolation.linear,
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
        temp.path[1] = {
            "position": [
                Line(
                    (x2, y2),
                    (x3, y3),
                ),
                particle_shake
            ],
            "interpolation_x": self.interpolation.remaining_approach,
            "interpolation_x_arg_a": fast,
            "interpolation_y": self.interpolation.remaining_approach,
            "interpolation_y_arg_a": fast,
            "steps": this_steps,
            "modules": {
                "fade": {
                    "interpolation": self.interpolation.linear,
                    "arg_a": None,
                    "object": Fade(
                        start_percentage=fade_intensity,
                        end_percentage=0,
                        finish_steps=this_steps,
                    )
                }
            }
        }

        temp.image.resize_by_ratio(
            random.uniform(0.1, 0.3),
            override=True
        )

        self.content[2].append(temp)

    def add_moving_background(self, shake=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation": self.interpolation.remaining_approach,
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "1 + 2*X",
                    "arg_a": 0.08,
                },
                "blur": {
                    "activation": 15,
                }
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "background.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width + (2 * shake),
            self.context.height + (2 * shake),
            override=True
        )

        self.content[0] = [temp]
    

    def add_static_background(self, shake=0): 

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation": self.interpolation.remaining_approach,
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "background.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width + (2 * shake),
            self.context.height + (2 * shake),
            override=True
        )

        self.content[0] = [temp]


    def add_layers_background(self, shake1=0, shake2=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake1, -shake1),
                Shake({
                    "interpolation": self.interpolation.remaining_approach,
                    "distance": shake1,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "1 + 4*X",
                    "arg_a": 0.04,
                },
                "blur": {
                    "activation": "max(5 - 15*X, 0)",
                }
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "layers" + os.path.sep + "space.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width + (2 * shake1),
            self.context.height + (2 * shake1),
            override=True
        )

        temp2 = MMVImage(self.context)
        temp2.path[0] = {
            "position": [
                Point(-shake2, -shake2),
                Shake({
                    "interpolation": self.interpolation.remaining_approach,
                    "distance": shake2,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "1 + 2*X",
                    "arg_a": 0.08,
                },
                "blur": {
                    "activation": "15*X",
                }
            }
        }
        temp2.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "layers" + os.path.sep + "curtains.png",
            # convert_to_png=True
        )
        temp2.image.resize_to_resolution(
            self.context.width + (2 * shake2),
            self.context.height + (2 * shake2),
            override=True
        )

        self.content[0] = [temp]
        self.content[1] = [temp2]


    def add_logo(self, shake=0):
        logo_size = int((200/1280)*self.context.width)
        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(
                    self.context.width // 2 - (logo_size/2),
                    self.context.height // 2 - (logo_size/2)
                ),
                Shake({
                    "interpolation": self.interpolation.remaining_approach,
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.04,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                })
            ],
            "steps": math.inf,
            "interpolation_x": None,
            "interpolation_y": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "1 + 8*X",
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

        self.content[3] = [temp]

    def add_visualizer(self):
        temp = MMVVisualizer(self.context)
        self.content[0].append(temp)
    
    def add_post_processing(self):
        vignetting_start = 900
        self.canvas.vignetting = vignetting_start
        self.canvas.post_processing[0] =  {
            "steps": math.inf,
            "modules": {
                "vignetting": {
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "%s - 8000*X" % vignetting_start,
                    "arg_a": 0.09,
                    "minimum": 600,
                }
            }
        }

    # Generate the objects on the animation
    # TODO: PROFILES, CURRENTLY MANUALLY SET HERE
    def generate(self):

        config = {
            "moving_background": False,
            "static_background": True,
            "layers_background": False,
            "logo": True,
            "visualizer": False,
            "add_post_processing": False
        }

        if config["moving_background"]:
            self.add_moving_background(
                shake = int((15/1280) * self.context.width)
            )
        
        if config["static_background"]:
            self.add_static_background(
                shake = int((15/1280) * self.context.width)
            )
        
        if config["layers_background"]:
            self.add_layers_background(
                shake1 = int((15/1280) * self.context.width),
                shake2 = int((10/1280) * self.context.width)
            )
        
        if config["logo"]:
            self.add_logo()

        if config["visualizer"]:
            self.add_visualizer()
        
        if config["add_post_processing"]:
            self.add_post_processing()

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
        
        self.canvas.next(fftinfo)
        
        if this_step % 5 == 0:
            # print("Adding particle")
            self.add_random_particle()

        
