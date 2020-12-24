"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

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

"""
Polar coordinates are another way of expressing points on a 2d grid.
Instead of saying point coordinate (x, y) we say as in (r, theta) 
whereas r is the distance from the polar ( the origin, center (0, 0) )
and theta the angle (in radians) to what direction you distance yourself
from the origin point.

For example, if r=3 and theta=pi, you end up in the point (-3, 0) because
you distanced yourself 3 units at the pi angle, 180 degrees.

Because of this we can make a rectangular triangle with sides X and Y,
hypotenuse size of r and angle theta, we can express the points as:

y = r.sin(theta)
x = r.cos(theta)
x² + y² = r²

if we divide y/x we have tan(theta) so

y/x = r.sin(theta) / r.cos(theta)
y/x = sin(theta) / cos(theta)
y/x = tan(theta)

I use this because it's easier to generate the visualization bars
with polar coordinates as you just have to set a angle according to the
frequency position on the ditionary and the size of the point is just the r
which is controlled by the FFT magnitude at that point
"""
class PolarCoordinates:

    def __init__(self) -> None:
        # Start at the point (0, 0)
        self.r = 0
        self.theta = 0
        self.round = 2

    def from_r_theta(self, r: float, theta: float) -> None:
        self.r = r
        self.theta = theta
    
    def from_rectangular(self, x: float, y: float) -> None:
        self.r, self.theta = self.rectangular_to_polar(x, y)

    def polar_to_rectangular(self, r: float, theta: float) -> list:
        # x = r.cos(theta)
        # y = r.sin(theta)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        return [round(x, self.round), round(y, self.round)]

    def rectangular_to_polar(self, x: float, y: float) -> list:
        # x = r.cos(theta) -> theta = cos-1 (x/r)
        # y = r.sin(theta) -> theta = sin-1 (y/r)
        # x² + y² = r² -> r = sqrt(x² + y²)
        r = (x**2 + y**2)**0.5
        theta = math.acos(x/r)
        return [round(r, self.round), round(theta, self.round)]
    
    def get_rectangular_coordinates(self) -> list:
        return self.polar_to_rectangular(self.r, self.theta)
