"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Modifiers (paths, effects, constants) we use under animations
Yes dataclasses would be better but welp

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

from mmv.mmvskia.mmv_interpolation import MMVSkiaInterpolation
from enum import Enum
import random
import math
import os


# Modes the path modifiers can use
class MMVSkiaModifierMode(Enum):
    OVERRIDE_VALUE_RESET_OFFSET = 1
    OVERRIDE_VALUE_KEEP_OFFSET_VALUE = 2
    ADD_TO_VALUE = 3
    OFFSET_VALUE = 4

# original_value: N-dimentional list or original values of the object
# original_offset: N-dimentional list or original offset values of the object
# modifier_value: N-dimentional list of the modifier values
def return_by_mode(mode, original_value: list, original_offset: list, modifier_value: list) -> list:
    
    # Override object's original value with modifier value and reset offset
    if mode == MMVSkiaModifierMode.OVERRIDE_VALUE_RESET_OFFSET:
        return [
            modifier_value,
            [0] * len(modifier_value),
        ]
    
    # Override object's original value but keep original offset
    elif mode == MMVSkiaModifierMode.OVERRIDE_VALUE_KEEP_OFFSET_VALUE:
        return [
            modifier_value,
            original_offset,
        ]

    # Add to object's original value, keep offset
    elif mode == MMVSkiaModifierMode.ADD_TO_VALUE:
        return [
            [a + b for a, b in zip(original_value, modifier_value)],
            original_offset
        ]
    
    # Keeps object original value, add to offset
    elif mode == MMVSkiaModifierMode.OFFSET_VALUE:
        return [
            original_value,
            [a + b for a, b in zip(original_offset, modifier_value)],
        ]



# # # # # [ PATHS ] # # # # #


"""
    From a point A to point B following an certain interpolation
    By default overrides the base position and keeps the offset
kwargs: {
    "start": list, 2d coordinate [x, y]
    "end": list, 2d coordinate [x, y]
    "interpolation_x": MMVSkiaInterpolation
    "interpolation_y": MMVSkiaInterpolation
    "mode": see return_by_mode and MMVSkiaModifierMode
}
"""
class MMVSkiaModifierLine:
    # @start, end: 2d coordinate list [0, 2]
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv

        self.start = kwargs["start"]
        self.end = kwargs["end"]
        self.interpolation_x = kwargs["interpolation_x"]
        self.interpolation_y = kwargs["interpolation_y"]
        self.mode = kwargs.get("mode", MMVSkiaModifierMode.OVERRIDE_VALUE_KEEP_OFFSET_VALUE)

        self.interpolation_x.init(self.start[1], self.end[1])
        self.interpolation_y.init(self.start[0], self.end[0])

    # Next step
    def next(self, x: float, y: float, ox: float, oy: float) -> list:

        # Calculate interpolation
        self.interpolation_x.next()
        self.interpolation_y.next()

        # Interpolation values into a list
        self.x = self.interpolation_x.current_value
        self.y = self.interpolation_y.current_value

        return return_by_mode(self.mode, [x, y], [ox, oy], [self.x, self.y])

"""
    Just a point, no interpolation
    By default overrides the base position and keeps the offset
kwargs: {
    "x": float, X coordinate of the point
    "y": float, Y coordinate of the point
    "mode": see return_by_mode and MMVSkiaModifierMode
}
"""
class MMVSkiaModifierPoint:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        
        # Get X, Y and mode, remember they are flipped
        self.x = kwargs["y"]
        self.y = kwargs["x"]
        self.mode = kwargs.get("mode", MMVSkiaModifierMode.OVERRIDE_VALUE_KEEP_OFFSET_VALUE)
    
    def next(self, x: float, y: float, ox: float, oy: float) -> list:
        return return_by_mode(self.mode, [x, y], [ox, oy], [self.x, self.y])

"""
    Shake modifier, walks randomly across a certain square area
    By default it keeps the base position, adds to the offset
kwargs: {
    "distance": float, maximum distance to walk on any direction (square)
    "interpolation_x": MMVSkiaInterpolation
    "interpolation_y": MMVSkiaInterpolation
    "mode": see return_by_mode and MMVSkiaModifierMode
}
"""
class MMVSkiaModifierShake:
    # @config: dict
    #    @"interpolation_$": Interpolation function on that $ axis
    #    @"arg_$": Interpolation argument letter $, see Interpolation class
    #    @"$_steps": How much steps to end interpolation
    #    @"distance": Max shake distance in any square direction
    #    
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv

        # Get config
        self.interpolation_x = kwargs["interpolation_x"]
        self.interpolation_y = kwargs["interpolation_y"]
        self.distance = kwargs["distance"]
        self.mode = kwargs.get("mode", MMVSkiaModifierMode.OFFSET_VALUE)

        # Start at the center point
        self.interpolation_x.start_value = 0
        self.interpolation_y.start_value = 0
        self.x = 0
        self.y = 0

        # Where we're going to interpolate next
        self.towards_x = 0
        self.towards_y = 0

        # Get a next random point as we're starting on (0, 0)
        self.next_random_point(who="both")
    
    # Generate a next random coordinate to shake to according to the max distance
    # @who: "x", "y" or "both"
    def next_random_point(self, who: str) -> None:
        if who == "x":
            self.towards_x = random.randint(-self.distance, self.distance)
        elif who == "y":
            self.towards_y = random.randint(-self.distance, self.distance)
        elif who == "both":
            self.next_random_point("x")
            self.next_random_point("y")
        
        self.interpolation_x.target_value = self.towards_x
        self.interpolation_y.target_value = self.towards_y

        self.interpolation_x.current_value = self.x
        self.interpolation_y.current_value = self.y
    
    # Next step of this X and Y towards the current random point
    # x: object's x coordinate
    # y: object's y coordinate
    # ox: object's x offset
    # oy: object's y offset
    def next(self, x: float, y: float, ox: float, oy: float) -> list:
        
        # Calculate next interpolation
        self.x = self.interpolation_x.next()

        if self.interpolation_x.finished:
            self.next_random_point("x")
            self.interpolation_x.finished = False

        # Calculate next interpolation
        self.y = self.interpolation_y.next()

        if self.interpolation_y.finished:
            self.next_random_point("y")
            self.interpolation_y.finished = False

        return return_by_mode(self.mode, [x, y], [ox, oy], [self.x, self.y])


# # # # # [ ROTATION ] # # # # #


# See MMVSkiaImageConfigure
class MMVSkiaModifierSineSwing:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        self.max_angle = kwargs["max_angle"]
        self.smooth = kwargs["smooth"]
        self.x = kwargs.get("phase", 0)
    
    # Return next value of the iteration, scaled by the fps
    def next(self) -> float:
        self.x += (1 / self.smooth) * self.mmv.context.fps_ratio_multiplier
        return self.max_angle * math.sin(self.x)

# See MMVSkiaImageConfigure
class MMVSkiaModifierLinearSwing:
    # @smooth: Add this part of 1 (1/smooth) on each next step to current X
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        self.smooth = kwargs["smooth"]
        self.x = kwargs.get("phase", 0)
    
    # Return next value of the iteration
    def next(self) -> float:
        self.x += (1 / self.smooth) * self.mmv.context.fps_ratio_multiplier
        return self.x


# # # # # [ VALUES ] # # # # #

"""
    Constant value, nothing changes
kwargs: {
    "value": float, the value :p
}
"""
class MMVSkiaModifierConstant:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        self.value = kwargs["value"]
    
    def next(self) -> float:
        return self.value


# # # # # [ 1D MODIFIERS ] # # # # #


# See MMVSkiaImageConfigure
class MMVSkiaModifierScalarResize:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        self.interpolation = kwargs["interpolation"]
        self.scalar = kwargs["scalar"]
        self.interpolation.start_value = 1

    def next(self) -> None:
        # Change interpolation target with scalar
        self.interpolation.target_value = 1 + (self.mmv.core.modulators["average_value"] * self.scalar)

        # Calculate next interpolation and assign to this value
        self.interpolation.next()
        self.value = self.interpolation.current_value

    def get_value(self) -> float:
        return self.value


"""
    Fade modifier, usually
kwargs: {
    "interpolation": MMVSkiaInterpolation
}
"""
# See MMVSkiaImageConfigure
class MMVSkiaModifierFade:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        self.interpolation = kwargs["interpolation"]
    
    def next(self) -> None:
        # Calculate next interpolation and assign to this value
        self.interpolation.next()
        self.value = self.interpolation.current_value

    def get_value(self) -> float:
        return self.value


"""
    Apply gaussian blur with this kernel size, average audio value multiplied by a ratio
kwargs: {
    "interpolation": MMVSkiaInterpolation
    "change_interpolation": bool, True, modify interpolation target values?
        "scalar": float: The scalar to multiply
            10: low
            15: medium
            20: high
}
"""
class MMVSkiaModifierGaussianBlur:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        self.interpolation = kwargs["interpolation"]
        self.change_interpolation = kwargs.get("change_interpolation", True)
        self.scalar = kwargs["scalar"]
        self.interpolation.start_value = 0
    
    def next(self) -> None:
        # Change interpolation target with scalar
        if self.change_interpolation:
            self.interpolation.target_value = self.mmv.core.modulators["average_value"] * self.scalar

        # Calculate next interpolation and assign to this value
        self.interpolation.next()
        self.value = self.interpolation.current_value

    def get_value(self) -> float:
        return self.value





# See MMVSkiaImageConfigure
class MMVSkiaModifierVignetting:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        self.interpolation = kwargs["interpolation"]
        self.start = kwargs["start"] * self.mmv.context.resolution_ratio_multiplier
        self.scalar = kwargs["scalar"] * self.mmv.context.resolution_ratio_multiplier
        self.minimum = kwargs["minimum"] * self.mmv.context.resolution_ratio_multiplier
        self.interpolation.start_value = 1

        self.center_function_x = kwargs.get("center_x", 
            MMVSkiaModifierConstant(self.mmv, value = self.mmv.context.width // 2)
        )
        self.center_function_y = kwargs.get("center_x", 
            MMVSkiaModifierConstant(self.mmv, value = self.mmv.context.height // 2)
        )

        self.interpolation.start_value = self.start

    def next(self) -> None:

        towards = self.start + (self.mmv.core.modulators["average_value"] * self.scalar)

        if towards < self.minimum:
            towards = self.minimum

        self.interpolation.target_value = towards

        # Calculate next interpolation and assign to this value
        self.interpolation.next()
        self.value = self.interpolation.current_value

    def get_value(self) -> float:
        return self.value

    def get_center(self) -> None:
        self.center_x = self.center_function_x.next()
        self.center_y = self.center_function_y.next()


