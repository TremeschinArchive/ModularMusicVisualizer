"""
===============================================================================

Purpose: SVG files utility

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

from wand.api import library
from io import BytesIO
from PIL import Image
import numpy as np
import wand.image
import wand.color
import cairosvg
import svgwrite
import pyvips
import sys
import cv2
import os


class SVG():
    def __init__(self, width, height, rasterizer, mode):
        self.width = width
        self.height = height
        self.rasterizer = rasterizer
        self.mode = mode
        self.SVG_ROUND = 4
            
    def new_drawing(self, centered=True):
        if centered:
            self.dwg = svgwrite.Drawing(
                viewBox=('%s %s %s %s' % (-self.width/2, -self.height/2, self.width, self.height))
            )
        else:
            self.dwg = svgwrite.Drawing(
                viewBox=('%s %s %s %s' % (0, 0, self.width, self.height))
            )

    # Return a PNG PIL Image from this object svg
    def get_png(self, convert_to_png=True):
        
        svg_string = self.dwg.tostring()

        svg = pyvips.Image.svgload_buffer(svg_string.encode())
        image = np.frombuffer(svg.write_to_memory(), dtype=np.uint8).reshape(self.width, self.height, 4) 

        return image
