"""
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

from mmv.common.cmn_functions import Functions
from mmv.common.cmn_types import *
import random


class Interpolation():

    def __init__(self):
        self.functions = Functions()

    # Linear, between point A and B based on a current "step" and total steps
    def linear(self,
            curret_value: Number,
            target_value: Number,
            current_step: Number,
            total_steps: Number,
        ) -> Number:

        if current_step > total_steps:
            return target_value
            
        part = (target_value - curret_value) / total_steps
        walked = part * current_step
        return curret_value + walked

    # "Biased" remaining linear
    # aggressive, 0.05 is smooth, 0.1 is medium, 1 is instant
    # random is a decimal that adds to aggressive randomly
    def remaining_approach(self,
            curret_value: Number,
            target_value: Number,
            current_step: Number,
            this_coord: Number,
            aggressive: Number,
            aggressive_randomness: Number=0,
        ) -> Number:

        # We're at the first step, so start on current value
        if current_step == 0:
            return curret_value

        return this_coord + ( (target_value - this_coord) * (aggressive + random.uniform(0, aggressive_randomness)) )

    # Sigmoid activation between two points, smoothed out "linear" curver
    def sigmoid(self,
            curret_value: Number,
            target_value: Number,
            current_step: Number,
            total_steps: Number,
            this_coord: Number,
            smooth: Number,
        ) -> Number:

        distance = (target_value - curret_value)
        where = self.functions.proportion(total, 1, current)
        walk = distance*self.functions.sigmoid(where, smooth)
        return a + walk
