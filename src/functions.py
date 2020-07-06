"""
===============================================================================

Purpose: Activation functions

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

import math


class Functions():

    # Sigmoid function, put that last part in a graphic visualization software to understand
    # @smooth: how much steps are needed for X to get from -4 to 4 on the function (as they are some nice angle spots on the graph)
    # @x: the "biased" "this_position" step
    def sigmoid(self, x, smooth):
        # Fit x from -4 to 4, 0 to 1
        fit = smooth*x - (smooth/2)
        return 1 / (1 + math.exp(-fit))

    # Calculate a linear proportion
    def proportion(self, a, b, c):
        # a - b
        # c - x
        # x = b*c/a
        return b*c/a
