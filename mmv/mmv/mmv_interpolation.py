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


class MMVInterpolation:
    def __init__(self, config: dict) -> None:
        # Config dictionary
        self.config = config

        # Generic interpolation
        self.interpolation = Interpolation()

        # Internal vars
        self.current_value = None
        self.target_value = None
        self.current_step = None

        self.configure()

    def configure(self) -> None:

        interpolation_function_name = self.config.get("function")

        if interpolation_function_name == "remaining_approach":
            # Set the function
            self.interpolation_function = self.interpolation.remaining_approach
            self.next_interpolation = self.remaining_approach

            # Options of the interpolation function
            self.aggressive = self.config["aggressive"]
            self.aggressive_randomness = self.config.get("aggressive_randomness")
        
        elif interpolation_function_name == "linear":
            # Set the function
            self.interpolation_function = self.interpolation.linear
            self.next_interpolation = self.linear

            # Options of the interpolation function
            self.total_steps = self.config.get("total_steps")

    def next(self) -> Number:
        self.current_step += 1
        return self.next_interpolation()
    
    def remaining_approach(self) -> None:
        self.interpolation_function(
            start_value = self.start_value
            target_value = self.target_value
            current_step = self.current_step
            current_value = self.current_value
            aggressive = self.aggressive
            aggressive_randomness = self.aggressive_randomness,
        )
    
    def linear(self) -> None:
        self.interpolation_function(
            start_value = self.start_value,
            target_value = self.target_value,
            current_step = self.current_step,
            total_steps = self.total_steps,
        )
