"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Interpolation simplifed for MMV

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

from mmv.common.cmn_interpolation import Interpolation
import math


"""
    Interpolation class, wraps around the cmn_interpolation stuff
kwargs: {
    "function": str, function name on class Interpolation

    For "function" = "remaining_approach":
        "ratio": float, ratio of the interpolation
        "ratio_randomness": float, 0, Add a random number from 0 to this to the ratio
        "speed_up_by_audio_volume": float, 0
            Change temporarily the ratio, adds audio average amplitude times this
}
"""
class MMVSkiaInterpolation:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv

        debug_prefix = "[MMVSkiaInterpolation.__init__]"

        # Generic interpolation
        self.interpolation = Interpolation()

        # Internal vars
        self.current_value = 0
        self.current_step = 0

        self.finished = False

        self.start_value = kwargs.get("start")
        self.target_value = kwargs.get("end")

        function = kwargs.get("function")

        # Get options for a remaining approach interpolation
        if function == "remaining_approach":
            # Set the function
            self.next_interpolation_function = self.remaining_approach

            # Options of the interpolation function
            self.ratio = kwargs["ratio"]
            self.ratio_randomness = kwargs.get("ratio_randomness", 0)
            self.speed_up_by_audio_volume = kwargs.get("speed_up_by_audio_volume", 0)
        
        # Get options for a linear interpolation
        elif function == "linear":
            # Set the function
            self.next_interpolation_function = self.linear

            # Options of the interpolation function
            self.total_steps = kwargs.get("total_steps") * self.mmv.context.fps_ratio_multiplier
        
        # Get options for a sigmoid interpolation
        elif function == "sigmoid":
            # Set the function
            self.next_interpolation_function = self.sigmoid

            # Options of the interpolation function
            self.smooth = kwargs.get("smooth") * self.mmv.context.fps_ratio_multiplier
        
        else:
            raise RuntimeError(debug_prefix, "Unknown function, kwargs:", kwargs)

    # If we want to find start and end value after creating the interpolation object
    def init(self, start_value: float, target_value: float) -> None:
        self.start_value = start_value
        self.target_value = target_value

    def set_target(self, value: float) -> None:
        self.target_value = value

    def next(self) -> float:
        self.current_value = self.next_interpolation_function()

        if abs(self.current_value - self.target_value) < 1:
            self.finished = True

        self.current_step += 1

        return self.current_value
    
    def remaining_approach(self) -> float:

        # Change the ratio according to the audio volume
        ratio = self.ratio + (self.mmv.core.modulators["average_value"] * self.speed_up_by_audio_volume)

        # https://gitlab.com/Tremeschin/modular-music-visualizer/-/issues/2
        # If new fps < 60, ratio should be higher
        #
        # Ratio = 0.5,  2x -> 1  0.5  0.25,        1x -> 0.75 , R = 0.25
        # Ratio = 0.5,  3x -> 1  0.5  0.25  0.125  1x -> 0.865, R = 0.125
        # Ratio = 0.5,  2x -> 1  0.5  0.25,        4x -> x^4 = 0.25,  x = 0.25**(1/4), 
        # (self.ratio**60)**(1/self.mmv.context.fps)
        #
        ratio_according_to_fps = 1 - ((1 - ratio)**(60 / self.mmv.context.fps))

        return self.interpolation.remaining_approach(
            start_value = self.start_value,
            target_value = self.target_value,
            current_step = self.current_step,
            current_value = self.current_value,
            ratio = ratio_according_to_fps,
            ratio_randomness = self.ratio_randomness,
        )
    
    def linear(self) -> float:
        return self.interpolation.linear(
            start_value = self.start_value,
            target_value = self.target_value,
            current_step = self.current_step,
            total_steps = self.total_steps,
        )
    
    def sigmoid(self) -> float:
        return self.interpolation.sigmoid(
            start_value = self.start_value,
            target_value = self.target_value,
            smooth = self.smooth,
        )
