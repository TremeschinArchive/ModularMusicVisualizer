"""
===============================================================================

Purpose: Canvas to draw on

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


class Canvas():
    def __init__(self, context):

        debug_prefix = "[Canvas.__init__]"

        self.context = context
        self.utils = Utils()

        self.reset_canvas()

    def reset_canvas(self):

        debug_prefix = "[Canvas.reset_canvas]"

        # Our Canvas is a black Frame class
        self.canvas = Frame()
        self.canvas.new(self.context.width, self.context.height, transparent=True)

        print(debug_prefix, "Create new frame as canvas")
