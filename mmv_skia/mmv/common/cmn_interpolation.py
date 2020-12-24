"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Interpolation file with step functions

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

import mmv.common.cmn_any_logger
from mmv.common.cmn_functions import Functions
import random


class Interpolation:
    def __init__(self):
        self.functions = Functions()

    """
        Linear, between point A and B based on a current "step" and total steps
    kwargs: {
        "start_value": float, target start value
        "target_value": float, target end value
        "current_step": float, this step out of the total
        "total_steps": float, target total steps to finish the interpolation
    }
    """
    def linear(self, **kwargs) -> float:

        # Out of bounds in steps, return target value
        if kwargs["current_step"] > kwargs["total_steps"]:
            return kwargs["target_value"]

        # How much a walked part is? difference between target and start, divided by total steps
        part = (kwargs["target_value"] - kwargs["start_value"]) / kwargs["total_steps"]

        # How much we walk from start to finish in that proportion
        walked = part * kwargs["current_step"]

        # Return the proportion walked plus the start value
        return kwargs["start_value"] + walked

    """
        "Biased" remaining linear, walks remaining distance times the ratio
        ratio, 0.05 is smooth, 0.1 is medium, 1 is instant
        random is a decimal that adds to ratio randomly
    
    kwargs: {
        "start_value": float, target start value (returned if current_step is zero)
        "target_value": float, target value to reach
        "current_step": float, only used if 0 to signal start of interpolation
        "current_value": float, the position we're at to calculate the remaining distance
        "ratio": float, walk remaining distance times this ratio from current value
        "ratio_randomness": float=0, add a random value from 0 to this to the ratio
    }
    """
    def remaining_approach(self, **kwargs) -> float:

        # We're at the first step, so start on current value
        if kwargs["current_step"] == 0:
            return kwargs["start_value"]

        # Remaining distance is difference between target and current, ratio is the ratio plus a random or 0 value
        remaining_distance = (kwargs["target_value"] - kwargs["current_value"])
        ratio = kwargs["ratio"] + random.uniform(0, kwargs.get("ratio_randomness", 0))

        return kwargs["current_value"] + (remaining_distance * ratio)

    # Sigmoid activation between two points, smoothed out "linear" curver
    def sigmoid(self,
            start_value: float,
            target_value: float,
            smooth: float,
        ) -> float:

        distance = (target_value - start_value)
        where = self.functions.proportion(total, 1, current)
        walk = distance * self.functions.sigmoid(where, smooth)
        return a + walk
