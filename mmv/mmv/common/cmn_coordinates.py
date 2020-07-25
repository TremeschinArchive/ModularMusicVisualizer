"""
===============================================================================

Purpose: Classes that define alternate coordinate systems

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


class PolarCoordinates():
    def __init__(self):
        # Start at the point (0, 0)
        self.r = 0
        self.theta = 0
        self.round = 2

    def from_r_theta(self, r, theta):
        self.r = r
        self.theta = theta
    
    def from_rectangular(self, x, y):
        self.r, self.theta = self.rectangular_to_polar(x, y)

    def polar_to_rectangular(self, r, theta):
        # x = r.cos(theta)
        # y = r.sin(theta)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        return [round(x, self.round), round(y, self.round)]

    def rectangular_to_polar(self, x, y):
        # x = r.cos(theta) -> theta = cos-1 (x/r)
        # y = r.sin(theta) -> theta = sin-1 (y/r)
        # x² + y² = r² -> r = sqrt(x² + y²)
        r = (x**2 + y**2)**0.5
        theta = math.acos(x/r)
        return [round(r, self.round), round(theta, self.round)]
    
    def get_rectangular_coordinates(self):
        return self.polar_to_rectangular(self.r, self.theta)
