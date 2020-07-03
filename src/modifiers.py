"""
===============================================================================

Purpose: Paths a few objects can follow

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

from utils import Utils
from frame import Frame
import os


# # Paths

class Line():
    def __init__(self, start, end, steps):
        self.start = start
        self.end = end

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y
    

# # Effects

class Fade():
    def __init__(self, start_percentage, end_percentage):
        self.start_percentage = start_percentage
        self.end_percentage = end_percentage