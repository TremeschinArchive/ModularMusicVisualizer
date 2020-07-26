"""
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
from mmv.common.cmn_functions import Functions
from mmv.common.cmn_types import *


class MMVInterpolation:
    def __init__(self, config: dict) -> None:
        # Config dictionary
        self.config = config

        # Generic interpolation
        self.interpolation = Interpolation()

        # Internal vars
        self.current_value = 0
        self.current_step = 0

        self.finished = False

        self.configure()

    def configure(self) -> None:

        self.start_value = self.config.get("start")
        self.target_value = self.config.get("end")

        interpolation_function_name = self.config.get("function")

        # Get options for a remaining approach interpolation
        if interpolation_function_name == "remaining_approach":
            # Set the function
            self.next_interpolation = self.remaining_approach

            # Options of the interpolation function
            self.aggressive = self.config["aggressive"]
            self.aggressive_randomness = self.config.get("aggressive_randomness", 0)
        

        # Get options for a linear interpolation
        elif interpolation_function_name == "linear":
            # Set the function
            self.next_interpolation = self.linear

            # Options of the interpolation function
            self.total_steps = self.config.get("total_steps")
        
        
        # Get options for a sigmoid interpolation
        elif interpolation_function_name == "sigmoid":
            # Set the function
            self.next_interpolation = self.sigmoid

            # Options of the interpolation function
            self.smooth = self.config.get("smooth")

    # If we want to find start and end value after creating the interpolation object
    def init(self, start_value: Number, target_value=Number) -> None:
        self.start_value = start_value
        self.target_value = target_value

    def next(self) -> Number:

        self.current_value = self.next_interpolation()

        if abs(self.current_value - self.target_value) < 1:
            self.finished = True

        self.current_step += 1

        return self.current_value
    
    def remaining_approach(self) -> Number:
        return self.interpolation.remaining_approach(
            start_value = self.start_value,
            target_value = self.target_value,
            current_step = self.current_step,
            current_value = self.current_value,
            aggressive = self.aggressive,
            aggressive_randomness = self.aggressive_randomness,
        )
    
    def linear(self) -> Number:
        return self.interpolation.linear(
            start_value = self.start_value,
            target_value = self.target_value,
            current_step = self.current_step,
            total_steps = self.total_steps,
        )
    
    def sigmoid(self) -> Number:
        return self.interpolation.sigmoid(
            start_value = self.start_value,
            target_value = self.target_value,
            smooth = self.smooth,
        )
