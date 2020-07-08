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
from functions import Functions
from mmvimage import MMVImage
from mmvgenerator import *
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

        self.interpolation = Interpolation()
        self.functions = Functions()
        self.utils = Utils()

        self.content = {}

        n_layers = 10
        for n in range(n_layers):
            self.content[n] = []

    def add_moving_background(self, shake=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation_x": self.interpolation.remaining_approach,
                    "interpolation_y": self.interpolation.remaining_approach,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
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
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "background2.jpg",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            self.context.width + (2 * shake),
            self.context.height + (2 * shake),
            override=True
        )

        self.content[0].append(temp)
    
    def add_moving_video_background(self, shake=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation_x": self.interpolation.remaining_approach,
                    "interpolation_y": self.interpolation.remaining_approach,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
                })
            ],
            "steps": math.inf,
            "interpolation_x": None, "interpolation_x_arg_a": None,
            "interpolation_y": None, "interpolation_y_arg_a": None,
            "modules": {
                "resize": {
                    "keep_center": True,
                    "interpolation": self.interpolation.remaining_approach,
                    "activation": "1 + 0.3*X",
                    "arg_a": 0.08,
                },
                "blur": {
                    "activation": "15*X",
                },
                "video": {
                    "path": self.context.ROOT + os.path.sep + "vid.mp4",
                    "shake": shake
                }
            }
        }
        
        self.content[0].append(temp)

    def add_static_background(self, shake=0): 

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake, -shake),
                Shake({
                    "interpolation_x": self.interpolation.remaining_approach,
                    "interpolation_y": self.interpolation.remaining_approach,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
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

        self.content[0].append(temp)

    def add_layers_background(self, shake1=0, shake2=0):

        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(-shake1, -shake1),
                Shake({
                    "interpolation_x": self.interpolation.remaining_approach,
                    "interpolation_y": self.interpolation.remaining_approach,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake1,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
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
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "layers" + os.path.sep + "nature.jpg",
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
                    "interpolation_x": self.interpolation.remaining_approach,
                    "interpolation_y": self.interpolation.remaining_approach,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake2,
                    "arg_a": 0.01,
                    "arg_b": 0.02,
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

        self.content[0].append(temp)
        self.content[1].append(temp2)

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
                    "interpolation_x": self.interpolation.remaining_approach,
                    "interpolation_y": self.interpolation.remaining_approach,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.04,
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
                },
                "rotate": {
                    "object": SineSwing(6, 100)
                }
            }
        }
        temp.image.load_from_path(
            self.context.assets + os.path.sep + "tremx_assets" + os.path.sep + "logo" + os.path.sep + "logo.png",
            convert_to_png=True
        )
        temp.image.resize_to_resolution(
            logo_size,
            logo_size,
            override=True
        )

        self.content[4] = [temp]

    def add_visualizer(self, shake=0):

        visualizer_size = int((720/1280)*self.context.width)
        
        temp = MMVImage(self.context)
        temp.path[0] = {
            "position": [
                Point(
                    self.context.width // 2 - (visualizer_size/2),
                    self.context.height // 2 - (visualizer_size/2)
                ),
                Shake({
                    "interpolation_x": self.interpolation.remaining_approach,
                    "interpolation_y": self.interpolation.remaining_approach,
                    "x_steps": "end_interpolation",
                    "y_steps": "end_interpolation",
                    "distance": shake,
                    "arg_a": 0.01,
                    "arg_b": 0.04,
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
                },
                "rotate": {
                    "object": LinearSwing(10)
                },
                "blur": {
                    "activation": "20*X",
                },
                "visualizer": {
                    "object": MMVVisualizer(
                        self.context,
                        {
                            "type": "circle",
                            "width": visualizer_size,
                            "height": visualizer_size,
                            "minimum_bar_distance": 100,
                            "maximum_bar_distance": 200,
                            "activation": {
                                "function": self.functions.sigmoid,
                                "arg_a": 10,
                            },
                            "fourier": {
                                "interpolation": {
                                    "function": self.interpolation.remaining_approach,
                                    "activation": "X",
                                    "arg_a": 0.34,
                                    "steps": math.inf
                                },
                                "fitfourier": {
                                    "fft_smoothing": 3,
                                    "tesselation": 2,
                                }
                            }
                        }
                    )
                }
            }
        }
        self.content[3].append(temp)
    
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
                    "minimum": 450,
                }
            }
        }

    def add_particles_generator(self):        
        generator = MMVParticleGenerator(self.context)
        self.content[0].append(generator)

    # Generate the objects on the animation
    # TODO: PROFILES, CURRENTLY MANUALLY SET HERE
    def generate(self):

        config = {
            "moving_background": False,
            "static_background": True,
            "layers_background": False,
            "moving_video_background": False,
            "logo": True,
            "visualizer": True,
            "add_post_processing": False,
            "particles": False
        }

        if config["moving_background"]:
            self.add_moving_background(
                shake = int((15/1280) * self.context.width)
            )
        
        if config["static_background"]:
            self.add_static_background()
        
        if config["layers_background"]:
            self.add_layers_background(
                shake1 = int((20/1280) * self.context.width),
                shake2 = int((10/1280) * self.context.width)
            )
        
        if config["moving_video_background"]:
            self.add_moving_video_background(
                shake = int((15/1280) * self.context.width)
            )
        
        if config["logo"]:
            self.add_logo()

        if config["visualizer"]:
            self.add_visualizer()
        
        if config["add_post_processing"]:
            self.add_post_processing()
        
        if config["particles"]:
            self.add_particles_generator()

    # Call every next step of the content animations
    def next(self, audio_slice, fft, this_step):

        # Calculate some fft from the audio
        biased_total_size = abs(sum(fft)) / self.context.batch_size
        average_value = sum([abs(x)/(2**self.audio.info["bit_depth"]) for x in audio_slice]) / len(audio_slice)

        fftinfo = {
            "average_value": average_value,
            "biased_total_size": biased_total_size,
            "fft": fft
        }

        # print(">>>>", fftinfo, audio_slice)

        for index in sorted(list(self.content.keys())):
            for item in self.content[index]:

                # We can delete the item as it has decided life wasn't worth anymore
                if item.is_deletable:
                    del item
                    continue

                # Generate next step of animation
                new = item.next(fftinfo, this_step)

                # Blit itself on the canvas
                item.blit(self.canvas)

                # Item is an MMVGenerator so we'll see what it has to offer
                if item.type == "mmvgenerator":
                    # The response object (if any [None]) and layer to instert on this self.content
                    new_object = new["object"]

                    # Object is not null, add it to the said layer
                    if not new_object == None:
                        self.content[new["layer"]].append(new_object)
    
        # Post process this final frame as we added all the items
        self.canvas.next(fftinfo)
