"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

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

import mmv.common.cmn_any_logger
import numpy as np
import math


class Functions:

    # Sigmoid function, put that last part in a graphic visualization software to understand
    # @smooth: how much steps are needed for X to get from -4 to 4 on the function (as they are some nice angle spots on the graph)
    # @x: the "biased" "this_position" step
    def sigmoid(self, x: float, smooth: float) -> float:
        # Fit x from -4 to 4, 0 to 1
        fit = smooth*x - (smooth/2)
        return 1 / (1 + math.exp(-fit))

    # Calculate a linear proportion
    def proportion(self, a: float, b: float, c: float) -> float:
        # a - b
        # c - x
        # x = b*c/a
        return b*c/a
    
    # We have two points P1 = (Xa, Ya) and P2 = (Xb, Yb)
    # It forms a line and we get a value of that line at X=get_x
    def value_on_line_of_two_points(self, Xa, Ya, Xb, Yb, get_x):
        # The slope is m = (Yb - Ya) / (Xb - Xa)
        # Starting from point Yb, we have Y - Yb = m(X - Xb)
        # so.. Y - Yb = ((Yb - Ya) / (Xb - Xa))(X - Xb)
        # And we want to isolate Y -->
        # Y = ((Yb - Ya) / (Xb - Xa))*(X - Xb) + Yb
        return ((Yb - Ya) / (Xb - Xa))*(get_x - Xb) + Yb

    # Smooth an array
    def smooth(self, array: np.ndarray, smooth: float):
        if smooth > 0:
            box = np.ones(smooth)/smooth
            array_smooth = np.convolve(array, box, mode='same')
            return array_smooth
        return array
    
    #
    # I wanted a function such that it gets evaluated with F(x, d, m) will have the properties:
    #
    # - F(0) = m
    # - F(x < d) < 1
    #
    # See: https://www.desmos.com/calculator/7omtsbxema
    #
    # There can be an improvement on controling the slope but that's a bit too much
    # for my applied maths intuition.
    #
    # This function is mainly used and interpreted as: the y value at this x will be
    # how much repeated music bars we'll render for the same frequency
    def how_much_bars_on_this_frequency(self, x, where_decay_less_than_one, value_at_zero):
        d = where_decay_less_than_one
        m = value_at_zero
        return m / ((x + (d/3)) * (1/(d/3)))
    