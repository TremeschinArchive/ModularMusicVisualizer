"""
===============================================================================

Purpose: MMVImage Configure object

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

from mmv.mmv_interpolation import MMVInterpolation
from mmv.mmv_visualizer import MMVVisualizer
from mmv.common.cmn_types import *
from mmv.mmv_modifiers import *
import os


"""
NOTE: The activation functions where a str is expected, it just evaluates
that expression and replaces "X" (capital letter x) with the average autio
amplitude at that point.

This will be documented properly in the future (I hope so)
"""

# Configure our main MMVImage, wrapper around animations
class MMVImageConfigure:

    # Get MMVImage object and set image index to zero
    def __init__(self, mmvimage_object) -> None:
        self.object = mmvimage_object
        self.animation_index = 0
    
    # Macros for initialializing this animation layer
    def init_animation_layer(self) -> None:
        self.set_animation_empty_dictionary()
        self.set_this_animation_steps()
        self.set_animation_position_interpolation(axis="both")
    
    # # # [ Load Methods ] # # #

    def load_image(self, path: str) -> None:
        self.object.image.load_from_path(path, convert_to_png=True)

    def load_video(self, path: str) -> None:
        self.add_module_video(path)

    # # # [ Resize Methods ] # # #

    def resize_to_resolution(self,
            width: Number,
            height: Number,
            override: bool=False
        ) -> None:

        self.object.image.resize_to_resolution(int(width), int(height), override=override)
    
    def resize_to_video_resolution(self, over_resize_x: int=0, over_resize_y: int=0) -> None:
        self.resize_to_resolution(
            width=self.object.context.width + over_resize_x,
            height=self.object.context.height + over_resize_y,
            override=True
        )

    # # # [ Set Methods ] # # #

    # Make an empty animation layer according to this animation index, dicitonaries
    def set_animation_empty_dictionary(self) -> None:
        self.object.animation[self.animation_index] = {}
        self.object.animation[self.animation_index]["position"] = {"path": []}
        self.object.animation[self.animation_index]["modules"] = {}
        self.object.animation[self.animation_index]["animation"] = {}
    
    # X and Y needs interpolation
    def set_animation_position_interpolation(self,
            axis: str="both",
            method=None,
            arg_a=None
        ) -> None:

        if axis == "both":
            for ax in ["x", "y"]:
                self.set_animation_position_interpolation(axis=ax)
        if not method in [None]:
            print("Unhandled interpolation method [%s]" % method)
            sys.exit(-1)
        
        self.object.animation[self.animation_index]["position"]["interpolation_%s" % axis] = method

    # Override current animation index we're working on into new index
    def set_animation_index(self, n: int) -> None:
        self.animation_index = n

    # How much steps in this animation
    def set_this_animation_steps(self, steps: float=math.inf) -> None:
        self.object.animation[self.animation_index]["animation"]["steps"] = steps

    # # # [ Next Methods ] # # #

    # Next animation index from the current one
    def next_animation_index(self) -> None:
        self.animation_index += 1
    
    # # # [ Add Methods ] # # #

    ## Generic add module ##
    def add_module(self, module: dict) -> None:
        module_name = list(module.keys())[0]
        print("Adding module", module, module_name)
        self.object.animation[self.animation_index]["modules"][module_name] = module[module_name]
    ## Generic add module ##

    # Add a Point modifier in the path
    def add_path_point(self, x: Number, y: Number) -> None:
        self.object.animation[self.animation_index]["position"]["path"].append(MMVModifierPoint(y, x))  # Invert y and x because numpy

    # TODO: Add path MMVModifierLine

    # Add a Gaussian Blur module, only need activation
    # Read comment at the beginning of this class
    def add_module_blur(self, activation: str) -> None:
        self.add_module({
            "blur": { "activation": activation }
        })
    
    # Add a glitch module
    def add_module_glitch(self,
            activation: str,
            color_offset: bool=False,
            scan_lines: bool=False
        ) -> None:

        self.add_module({
            "glitch": {
                "activation": activation,
                "color_offset": color_offset,
                "scan_lines": scan_lines,
            }
        })
    
    # Add a video module, be sure to match the FPS of both the outpu
    def add_module_video(self, path: str) -> None:
        self.add_module({
            "video": {
                "path": path
            }
        })
    
    # Add a rotate module with an modifier object with next function
    def add_module_rotate(self, modifier: Union[MMVModifierSineSwing, MMVModifierLinearSwing]) -> None:
        self.add_module({
            "rotate": {
                "object": modifier
            }
        })
    
    # Is this even python?
    def add_module_visualizer(self, 
            vis_type: str,
            vis_mode: str,
            width: int, height: int,
            minimum_bar_size: Number,
            activation_function,
            fourier_interpolation_function,
            pre_fft_smoothing: int,
            pos_fft_smoothing: int,
            subdivide: int
        ) -> None:

        self.add_module({
            "visualizer": {
                "object": MMVVisualizer(
                    self.object.context,
                    {
                        "type": vis_type,
                        "mode": vis_mode,
                        "width": width,
                        "height": height,
                        "minimum_bar_size": minimum_bar_size,
                        "activation": {
                            "function": activation_function,
                        },
                        "fourier": {
                            "interpolation": {
                                "function": fourier_interpolation_function,
                            },
                            "fitfourier": {
                                "pre_fft_smoothing": pre_fft_smoothing,
                                "pos_fft_smoothing": pos_fft_smoothing,
                                "subdivide": subdivide,
                            }
                        }
                    }
                )
            }
        })
    
    # Add resize by ratio module
    def add_module_resize(self,
            keep_center: bool,
            interpolation,
            activation: str,
            start_value: Number=1,
        ) -> None:

        self.add_module({
            "resize": {
                "object": MMVModifierScalarResize(
                    activation = activation,
                    interpolation = interpolation,
                    start_value = start_value
                ),
                "keep_center": True,
            }
        })
    
    # Add vignetting module with minimum values
    def add_module_vignetting(self,
            minimum: Number,
            activation: str,
            center_function_x,
            center_function_y,
            start_value=0
        ) -> None:

        self.add_module({
            "vignetting": {
                "object": MMVModifierVignetting(
                    minimum = minimum,
                    activation = activation,
                    center_function_x = center_function_x,
                    center_function_y = center_function_y,
                    start_value=start_value,
                    interpolation = MMVInterpolation({
                        "function": "remaining_approach",
                        "aggressive": 0.09,
                    }),
                ),
            },
        })


    # # # # [ Pre defined simple modules ] # # # #

    # Just add a vignetting module without much trouble with an intensity
    def simple_add_vignetting(self,
            intensity: str="medium",
            center: str="centered",
            activation: bool=None,
            center_function_x=None,
            center_function_y=None,
            start_value: Number=900
        ) -> None:

        intensities = {
            "low": "0",
            "medium": "%s - 4000*X" % start_value,
            "high": "0",
            "custom": activation
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled resize intensity [%s]" % intensity)
            sys.exit(-1)

        if center == "centered":
            center_function_x = MMVModifierConstant(self.object.image.width // 2)
            center_function_y = MMVModifierConstant(self.object.image.height // 2)

        self.add_module_vignetting(
            minimum = 450,
            activation = intensities[intensity],
            center_function_x = center_function_x,
            center_function_y = center_function_y,
            start_value=start_value,
        )

    # Add a visualizer module
    def simple_add_visualizer_circle(self,
            minimum_bar_size: Number,
            width: Number,
            height: Number,
            mode: str="symetric",
            responsiveness: Number=0.25,
            pre_fft_smoothing: int=2,
            pos_fft_smoothing: int=0,
            subdivide:int=2
        ) -> None:

        self.add_module_visualizer(
            vis_type = "circle", vis_mode = mode,
            width = width, height = height,
            minimum_bar_size = minimum_bar_size,
            activation_function = self.object.functions.sigmoid,
            fourier_interpolation_function = MMVInterpolation({
                "function": "sigmoid",
                "smooth": responsiveness,
            }),
            pre_fft_smoothing = pre_fft_smoothing,
            pos_fft_smoothing = pos_fft_smoothing,
            subdivide = subdivide
        )
    
    # Add a shake modifier on the pathing
    def simple_add_path_modifier_shake(self,
            shake_max_distance: Number,
            x_smoothness: Number=0.01,
            y_smoothness: Number=0.02
        ) -> None:

        self.object.animation[self.animation_index]["position"]["path"].append(
            MMVModifierShake(
                interpolation_x = MMVInterpolation({
                    "function": "remaining_approach",
                    "aggressive": x_smoothness,
                }),
                interpolation_y = MMVInterpolation({
                    "function": "remaining_approach",
                    "aggressive": y_smoothness,
                }),
                distance = shake_max_distance,
            )
        )
    
    # Blur the object based on an activation function
    def simple_add_linear_blur(self,
            intensity: str="medium",
            custom: str=""
        ) -> None:

        intensities = {
            "low": "10*X",
            "medium": "15*X",
            "high": "20*X",
            "custom": custom
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled blur intensity [%s]" % intensity)
            sys.exit(-1)
            
        self.add_module_blur(intensities[intensity])
    
    # Add simple glitch effect based on an activation function
    def simple_add_glitch(self,
            intensity: str="medium",
            color_offset: bool=False,
            scan_lines: bool=False
        ) -> None:

        intensities = {
            "low": "10*X",
            "medium": "15*X",
            "high": "20*X",
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled blur intensity [%s]" % intensity)
            sys.exit(-1)
            
        self.add_module_glitch(
            activation = intensities[intensity],
            color_offset = color_offset,
            scan_lines = scan_lines
        )
    
    # Add simple linear resize based on an activation function
    def simple_add_scalar_resize(self,
            intensity: str="medium",
            smooth: Number=0.08,
            activation: bool=None
        ) -> None:

        intensities = {
            "low": "1 + 0.5*X",
            "medium": "1 + 2.5*X",
            "high": "1 + 4*X",
            "custom": activation
        }
        if not intensity in list(intensities.keys()):
            raise RuntimeError("Unhandled resize intensity [%s]" % intensity)

        self.add_module_resize(
            keep_center = True,
            interpolation = MMVInterpolation({
                "function": "remaining_approach",
                "aggressive": smooth,
                "start": 1,
            }),
            activation = intensities[intensity],
        )
    
    # Add simple swing rotation, go back and forth
    def simple_add_swing_rotation(self,
            max_angle: Number=6,
            smooth: Number=100
        ) -> None:

        self.add_module_rotate( MMVModifierSineSwing(max_angle, smooth) )
    
    # Rotate to one direction continuously
    def simple_add_linear_rotation(self, smooth: int=10) -> None:
        self.add_module_rotate( MMVModifierLinearSwing(smooth) )