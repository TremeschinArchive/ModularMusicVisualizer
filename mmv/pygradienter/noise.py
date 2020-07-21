"""
===============================================================================

Purpose: Noise utils for more organic PyGradient images

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

from opensimplex import OpenSimplex
import random


# Functions to get some noise component 
class Noise():

    # Use opensimplex and create a simplex object
    def new_simplex(self, stretch_x, stretch_y, seed=random.randint(1,10000000)):
        self.simplex = OpenSimplex(seed=seed)
        self.stretch_x = stretch_x
        self.stretch_y = stretch_y

    # Get a simplex noise value on a given X and Y coordinate, apply stretch
    def get_simplex2d(self, x, y):
        return self.simplex.noise2d(x=x/self.stretch_x, y=y/self.stretch_y)