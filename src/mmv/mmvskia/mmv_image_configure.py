"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVSkiaImage Configure object, this is mainly a refactor of a .configure
method on MMVSkiaImage

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
from mmv.mmvskia.mmv_interpolation import MMVSkiaInterpolation
from mmv.mmvskia.mmv_vectorial import MMVSkiaVectorial
from mmv.mmvskia.mmv_modifiers import *
import logging
import math
import sys


# Configure our main MMVSkiaImage, wrapper around animations
class MMVSkiaImageConfigure:

    # Get MMVSkiaImage object and set image index to zero
    def __init__(self, mmvskia_main, mmvimage_object) -> None:
        self.mmvskia_main = mmvskia_main
        self.preludec = self.mmvskia_main.prelude["mmvimage_configure"]

        self.parent_object = mmvimage_object

        self.identifier = self.parent_object.identifier
        self.animation_index = 0

    # # # [ Load Image ] # # #

    def load_image(self, path: str, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.load_image]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Get absolute and real path
        path = self.mmvskia_main.utils.get_abspath(path, depth = ndepth, silent = not self.preludec["load_image"]["log_get_abspath"])

        # Log action
        if self.preludec["load_image"]["log_action"]:
            logging.info(f"{depth}{debug_prefix} [{self.identifier}] Loading image from path [{path}]")

        # Fail safe get the abspath and 
        self.parent_object.image.load_from_path(
            path, convert_to_png = True
        )

    # # # [ Dealing with animation ] # # #

    # Macros for initializing this animation layer
    def init_animation_layer(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.init_animation_layer]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log info and run routine functions
        if self.preludec["init_animation_layer"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Initializing animation layer")

        ndepth += LOG_NEXT_DEPTH

        # Reset animation layer and set an infinite amount of steps
        self.start_or_reset_this_animation(depth = ndepth)
        self.set_this_animation_steps(steps = math.inf, depth = ndepth)

    # Make an empty animation layer according to this animation index, dictionaries, RESETS EVERYTHING
    def start_or_reset_this_animation(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.start_or_reset_this_animation]"
        ndepth = depth + LOG_NEXT_DEPTH

        if self.preludec["start_or_reset_this_animation"]["log_action"]:
            logging.info(f"{depth}{debug_prefix} [{self.identifier}] Reset the parent MMVSkiaImage object animation layers")

        # Emptry layer of stuff
        self.parent_object.animation[self.animation_index] = {}
        self.parent_object.animation[self.animation_index]["position"] = {"path": []}
        self.parent_object.animation[self.animation_index]["modules"] = {}
        self.parent_object.animation[self.animation_index]["animation"] = {}

    # Override current animation index we're working on into new index
    def set_animation_index(self, n: int, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.set_animation_index]"
        ndepth = depth + LOG_NEXT_DEPTH

        if self.preludec["set_animation_index"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Set animation index N = [{n}]")

        self.animation_index = n

    # How much steps in this animation  
    def set_this_animation_steps(self, steps: float, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.set_this_animation_steps]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Hard debug
        if self.preludec["set_this_animation_steps"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] This animation N = [{self.animation_index}] will have [{steps}] steps")

        self.parent_object.animation[self.animation_index]["animation"]["steps"] = steps

    # Work on next animation index from the current one
    def next_animation_index(self) -> None:
        self.animation_index += 1

    # # # [ Resize Methods ] # # #

    # Resize this Image (doesn't work with Video) to this resolution
    # kwargs: { "width": float, "height": float, "override": bool, False }
    def resize_image_to_resolution(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.resize_image_to_resolution]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["resize_image_to_resolution"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Resize image to resolution, kwargs: {kwargs}")

        self.parent_object.image.resize_to_resolution(
            width = kwargs["width"],
            height = kwargs["height"],
            override = kwargs.get("override", False)
        )

    # kwargs: { "over_resize_width": float, 0, "over_resize_height": float, 0, "override": bool, True}
    # Over resizes mainly because Shake modifier
    def resize_image_to_video_resolution(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.resize_image_to_video_resolution]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["resize_image_to_video_resolution"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Resize image to video, kwargs: {kwargs}")

        self.resize_image_to_resolution(
            width = self.parent_object.mmvskia_main.context.width + kwargs.get("over_resize_width", 0),
            height = self.parent_object.mmvskia_main.context.height + kwargs.get("over_resize_height", 0),
            override = kwargs.get("override", True)
        )

    # # # [ Add Methods ] # # #

    """     (MODULE)
        Video module, images will be loaded and updated at each frame
        Please match the input video frame rate with the target FPS
    kwargs: {
        "path": str, Path to load the video
        "width", "height": float
            Width and height to scale the images of the video to (before any modification)
        "over_resize_width", "over_resize_height": float, 0
            Adds to the width and height to resize a bit more, a bleed
    }
    """
    def add_module_video(self, depth = LOG_NO_DEPTH, **kwargs):
        debug_prefix = "[MMVSkiaImageConfigure.add_module_video]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_module_video"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add video module, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["modules"]["video"] = {
            "path": kwargs["path"],
            "width": kwargs["width"] + kwargs.get("over_resize_width", 0),
            "height": kwargs["height"] + kwargs.get("over_resize_height", 0),
        }


    """     (PATH)
        Add a Point modifier in the path
    kwargs: {
        x: float, X coordinate
        y: float, Y coordinate
    }
    """
    def add_path_point(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_path_point]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_path_point"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add path point, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["position"]["path"].append(
            MMVSkiaModifierPoint(
                self.mmvskia_main,
                y = kwargs["y"], x = kwargs["x"],
            )
        )


    """     (PATH OFFSET)
        Add a shake modifier on the path, remaining approach interpolation
    kwargs: {
        "shake_max_distance": float, max distance on a square we walk on the shake
        "x_smoothness", "y_smoothness": float
            Remaining approach ratio
    }
    """
    def simple_add_path_modifier_shake(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.simple_add_path_modifier_shake]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["simple_add_path_modifier_shake"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add simple shaker modifier, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["position"]["path"].append(
            MMVSkiaModifierShake(
                self.mmvskia_main,
                interpolation_x = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = kwargs["x_smoothness"],
                ),
                interpolation_y = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = kwargs["y_smoothness"],
                ),
                distance = kwargs["shake_max_distance"],
            )
        )

    # # # [ MMVSkiaVectorial ] # # #

    """     (MMVSkiaVectorial)
    Adds a MMVSkiaVectorial with configs on kwargs (piano roll, progression bar, music bars)
    """
    def add_vectorial_by_kwargs(self, depth = LOG_NO_DEPTH, **kwargs):
        debug_prefix = "[MMVSkiaImageConfigure.add_vectorial_by_kwargs]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_vectorial_by_kwargs"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add vectorial module by kwargs, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["modules"]["vectorial"] = {
            "object": MMVSkiaVectorial(
                self.parent_object.mmvskia_main,
                **kwargs,
            )
        }

    """     (MMVSkiaVectorial), Music Bars
        Add a music bars visualizer module
    kwargs: configuration, see MMVSkiaMusicBarsVectorial class on MMVSkiaVectorial
    """
    def add_module_visualizer(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_visualizer]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Talk to MMVSkiaVectorial, say this is a visualizer and add MMVSkiaVectorial
        kwargs["vectorial_type_class"] = "visualizer"

        # Log action
        if self.preludec["add_module_visualizer"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Changed kwargs vectorial_type_class, new kwargs and call add_vectorial_by_kwargs: {kwargs}")

        self.add_vectorial_by_kwargs(depth = ndepth, **kwargs)
        
    """     (MMVSkiaVectorial), Progression Bar
        Add a progression bar module
    kwargs: configuration, see MMVSkiaProgressionBarVectorial class on MMVSkiaVectorial
    """
    def add_module_progression_bar(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_progression_bar]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Talk to MMVSkiaVectorial, say this is a progression bar and add MMVSkiaVectorial
        kwargs["vectorial_type_class"] = "progression-bar"

        # Log action
        if self.preludec["add_module_progression_bar"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Changed kwargs vectorial_type_class, new kwargs and call add_vectorial_by_kwargs: {kwargs}")

        self.add_vectorial_by_kwargs(**kwargs)

    """     (MMVSkiaVectorial), Piano Roll
        Add a piano roll module
    kwargs: configuration, see MMVSkiaPianoRollVectorial on MMVSkiaVectorial
    """
    def add_module_piano_roll(self, depth = LOG_NO_DEPTH, **kwargs) -> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_piano_roll]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Talk to MMVSkiaVectorial, say this is a piano roll and add MMVSkiaVectorial
        kwargs["vectorial_type_class"] = "piano-roll"

        # Log action
        if self.preludec["add_module_piano_roll"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Changed kwargs vectorial_type_class, new kwargs and call add_vectorial_by_kwargs: {kwargs}")

        self.add_vectorial_by_kwargs(**kwargs)



    # # # [ Modifiers ] # # #


    """     (MMVModifier), Resize
        Resize this object by the average audio value multiplied by a ratio 
    kwargs: {
        "keep_center": bool, True, resize and keep center
        
        "smooth": float, How smooth the resize will be, higher = more responsive, faster
        "scalar": float: The scalar to multiply
            0.5: low
            1:   low-medium
            2:   medium
            3:   medium-plus
            4:   high
            4.5: high-plus
    }
    """
    def add_module_resize(self, depth = LOG_NO_DEPTH, **kwargs)-> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_resize]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_module_resize"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add module resize, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["modules"]["resize"] = {
            "object": MMVSkiaModifierScalarResize(
                self.mmvskia_main,
                interpolation = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = kwargs["smooth"],
                ),
                **kwargs
            ),
            "keep_center": kwargs.get("keep_center", True),
        }

    
    """     (MMVModifier), Blur
        Apply gaussian blur with this kernel size, average audio value multiplied by a ratio
    kwargs: {
        "smooth": float, How smooth the blur will be, higher = more responsive, faster
        "scalar": float: The scalar to multiply
            10: low
            15: medium
            20: high
    }
    """
    def add_module_blur(self, depth = LOG_NO_DEPTH, **kwargs)-> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_blur]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_module_blur"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add module blur, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["modules"]["blur"] = {
            "object": MMVSkiaModifierGaussianBlur(
                self.mmvskia_main,
                interpolation = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = kwargs["smooth"],
                ),
                **kwargs
            ),
            "keep_center": kwargs.get("keep_center", True),
        }


    # # # [ Rotation ] # # #


    """     (MMVModifier), Rotation
        Add simple swing rotation, go back and forth
    kwargs: {
        "max_angle": float, maximum angle in radians to rotate
        "smooth": float, on each step, add this value to our sinewave point we get the values from
        "phase": float, 0, start the sinewave with a certain phase in radians?
    }
    """
    def add_module_swing_rotation(self, depth = LOG_NO_DEPTH, **kwargs)-> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_swing_rotation]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_module_swing_rotation"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add module swing rotation, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["modules"]["rotate"] = {
            "object": MMVSkiaModifierSineSwing(self.mmvskia_main, **kwargs)
        }


    """     (MMVModifier), Rotation
        Rotate to one direction continuously
    kwargs: {
        "smooth": float, on each step, add this value to our sinewave point we get the values from
        "phase": float, 0, start the sinewave with a certain phase in radians?
    }
    """
    def add_module_linear_rotation(self, depth = LOG_NO_DEPTH, **kwargs)-> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_linear_rotation]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_module_linear_rotation"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add module linear rotation, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["modules"]["rotate"] = {
            "object": MMVSkiaModifierLinearSwing(self.mmvskia_main, **kwargs)
        }


    """     (MMVModifier), Vignetting
        Black borders around the video
    kwargs: {
        "start": float, base value of the vignetting
        "scalar": float, hange the vignetting intensity by average audio amplitude by this
        "minimum": float, hard limit minimum vignette
        "smooth": float, how smooth changing values are on the interpolation
    }
    """
    def add_module_vignetting(self, depth = LOG_NO_DEPTH, **kwargs)-> None:
        debug_prefix = "[MMVSkiaImageConfigure.add_module_vignetting]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["add_module_vignetting"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add module linear rotation, kwargs: {kwargs}")

        self.parent_object.animation[self.animation_index]["modules"]["vignetting"] = {
            "object": MMVSkiaModifierVignetting(
                self.mmvskia_main,
                interpolation = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = kwargs["smooth"],
                ),
                **kwargs
            ),
        }

