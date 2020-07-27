"""
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

from mmv.mmv_interpolation import MMVInterpolation
from mmv.common.cmn_utils import Utils
from mmv.common.cmn_frame import Frame
from mmv.common.cmn_types import *
from enum import Enum
import random
import math
import os


# Modes the path modifiers can use
class ModifierMode(Enum):
    OVERRIDE_VALUE_RESET_OFFSET = 1
    OVERRIDE_VALUE_KEEP_OFFSET_VALUE = 2
    ADD_TO_VALUE = 3
    OFFSET_VALUE = 4

# original_value: N-dimentional list or original values of the object
# original_offset: N-dimentional list or original offset values of the object
# modifier_value: N-dimentional list of the modifier values
def return_by_mode(mode, original_value: list, original_offset: list, modifier_value: list) -> list:
    
    # Override object's original value with modifier value and reset offset
    if mode == ModifierMode.OVERRIDE_VALUE_RESET_OFFSET:
        return [
            modifier_value,
            [0] * len(modifier_value),
        ]
    
    # Override object's original value but keep original offset
    elif mode == ModifierMode.OVERRIDE_VALUE_KEEP_OFFSET_VALUE:
        return [
            modifier_value,
            original_offset,
        ]

    # Add to object's original value, keep offset
    elif mode == ModifierMode.ADD_TO_VALUE:
        return [
            [a + b for a, b in zip(original_value, modifier_value)],
            original_offset
        ]
    
    # Keeps object original value, add to offset
    elif mode == ModifierMode.OFFSET_VALUE:
        return [
            original_value,
            [a + b for a, b in zip(original_offset, modifier_value)],
        ]

# # Paths

# Basic

class MMVModifierLine:
    # @start, end: 2d coordinate list [0, 2]
    def __init__(self, 
            start: list,
            end: list,
            interpolation_x: MMVInterpolation,
            interpolation_y: MMVInterpolation,
            mode = ModifierMode.OVERRIDE_VALUE_KEEP_OFFSET_VALUE,

        ) -> None:

        self.start = start
        self.end = end
        self.interpolation_x = interpolation_x
        self.interpolation_y = interpolation_y
        self.mode = mode

        self.interpolation_x.init(start[1], end[1])
        self.interpolation_y.init(start[0], end[0])

    # Next step
    def next(self, x: Number, y: Number, ox: Number, oy: Number) -> list:

        # Calculate interpolation
        self.interpolation_x.next()
        self.interpolation_y.next()

        # Interpolation values into a list
        self.x = self.interpolation_x.current_value
        self.y = self.interpolation_y.current_value

        return return_by_mode(self.mode, [x, y], [ox, oy], [self.x, self.y])

class MMVModifierPoint:
    def __init__(self,
            x: Number,
            y: Number,
            mode = ModifierMode.OVERRIDE_VALUE_KEEP_OFFSET_VALUE,
        ) -> None:

        self.x = x
        self.y = y
        self.mode = mode
    
    def next(self, x: Number, y: Number, ox: Number, oy: Number) -> list:
        return return_by_mode(self.mode, [x, y], [ox, oy], [self.x, self.y])

# Linear Algebra / "Physics" / motion?

class VelocityVector:
    def __init__(self, x: Number, y: Number) -> None:
        self.x = x
        self.y = y

class MMVModifierShake:
    # @config: dict
    #    @"interpolation_$": Interpolation function on that $ axis
    #    @"arg_$": Interpolation argument letter $, see Interpolation class
    #    @"$_steps": How much steps to end interpolation
    #    @"distance": Max shake distance in any square direction
    #    
    def __init__(self,
            distance: Number,
            interpolation_x: MMVInterpolation,
            interpolation_y: MMVInterpolation,
            mode = ModifierMode.OFFSET_VALUE,
        ) -> None:

        # Get config
        self.interpolation_x = interpolation_x
        self.interpolation_y = interpolation_y
        self.distance = distance
        self.mode = mode

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
    def next(self, x: Number, y: Number, ox: Number, oy: Number) -> list:
        
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

# Swing back and forth in the lines of a sine wave
class MMVModifierSineSwing:
    # @max_value: Maximum amplitute of the sine wave
    # @smooth: Add this part of 1 (1/smooth) on each next step to current X
    def __init__(self, max_value: Number, smooth: Number) -> None:
        self.smooth = smooth
        self.max_value = max_value
        self.x = 0
    
    # Return next value of the iteration
    def next(self) -> Number:
        self.x += 1 / self.smooth
        return self.max_value * math.sin(self.x)


# Swing to one direction
class MMVModifierLinearSwing:
    # @smooth: Add this part of 1 (1/smooth) on each next step to current X
    def __init__(self, smooth: Number) -> None:
        self.smooth = smooth
        self.x = 0
    
    # Return next value of the iteration
    def next(self) -> Number:
        self.x += 1 / self.smooth
        return self.x

# # Values

class MMVModifierConstant:
    def __init__(self, value: Number) -> None:
        self.value = value
    
    def next(self) -> Number:
        return self.value

# # Effects

class MMVModifierVignetting:
    def __init__(self,
            minimum: Number,
            activation: str,
            center_function_x,
            center_function_y,
            interpolation,
            start_value: Number=0
        ) -> None:

        self.minimum = minimum
        self.activation = activation
        self.center_function_x = center_function_x
        self.center_function_y = center_function_y
        self.center_x = 0
        self.center_y = 0
        self.interpolation = interpolation
        self.interpolation.start_value = start_value
        self.value = 0
        
    def next(self, value: Number) -> None:

        value = eval( self.activation.replace("X", str(value)) )

        if value < self.minimum:
            self.towards = self.minimum
        else:
            self.towards = value
        
        self.interpolation.target_value = self.towards
        self.interpolation.next()
        self.value = self.interpolation.current_value

    def get_value(self) -> Number:
        return self.value

    def get_center(self) -> None:
        self.center_x = self.center_function_x.next()
        self.center_y = self.center_function_y.next()


from mmv.modifier_activators.ma_scalar_resize import *

class MMVModifierScalarResize:
    def __init__(self,
            interpolation: MMVInterpolation,
            start_value: Number,
            interpolation_changer,
            value_changer,
        ) -> None:

        self.interpolation = interpolation
        self.interpolation.start_value = start_value
        self.interpolation_changer = interpolation_changer
        self.value_changer = value_changer

    def next(self, average_audio_value: Number) -> None:
        self.interpolation_changer(
            interpolation = self.interpolation,
            average_audio_value = average_audio_value,
        )

        self.interpolation.next()

        self.value = self.value_changer(
            interpolation = self.interpolation,
            average_audio_value = average_audio_value,
        )

    def get_value(self) -> Number:
        return self.value


from mmv.modifier_activators.ma_fade import *

class MMVModifierFade:
    def __init__(self,
            interpolation,
            interpolation_changer = ma_fade_ic_keep,
            value_changer = ma_fade_vc_only_interpolation,
        ) -> None:

        self.interpolation = interpolation

        self.interpolation_changer = interpolation_changer
        self.value_changer = value_changer

    def next(self, average_audio_value: Number) -> None:
        self.interpolation_changer(
            interpolation = self.interpolation,
            average_audio_value = average_audio_value,
        )

        self.interpolation.next()
        
        self.value = self.value_changer(
            interpolation = self.interpolation,
            average_audio_value = average_audio_value,
        )

    def get_value(self) -> Number:
        return self.value
