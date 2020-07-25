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


class MMVInterpolation():
    def __init__(self, config: dict) -> None:
        self.interpolation = Interpolation()
        self.config = config

        # Internal vars
        self.current_value = None
        self.target_value = None
        self.current_step = None

    def configure(self) -> None:
        if self.config["function"] == "remaining_approach":
            self.interpolation_function = self.interpolation.remaining_approach
        
    def next(self) -> None:
