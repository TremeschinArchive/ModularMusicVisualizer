"""
===============================================================================

Purpose: MMVVisualizer object

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

from coordinates import PolarCoordinates
from interpolation import Interpolation
from functions import Functions
from resampy import resample
from modifiers import *
from frame import Frame
from utils import Utils
from svg import SVG
import svgwrite
import random
import math
import os

import numpy as np

class MMVVisualizer():
    def __init__(self, context, config):
        
        debug_prefix = "[MMVVisualizer.__init__]"
        
        self.context = context
        self.config = config

        self.functions = Functions()
        self.utils = Utils()
        self.svg = SVG(
            self.config["width"],
            self.config["height"],
            "cairo", #self.context.svg_rasterizer, # cairo is just faster here
            "png"
        )

        self.path = {}

        self.x = 0
        self.y = 0
        self.size = 1
        self.current_animation = 0
        self.current_step = 0
        self.is_deletable = False
        self.offset = [0, 0]
        self.polar = PolarCoordinates()

        self.current_fft = None

        # Create Frame and load random particle
        self.image = Frame()

    def smooth(self, array, smooth):
        box = np.ones(smooth)/smooth
        array_smooth = np.convolve(array, box, mode='same')
        return array_smooth

    # Next step of animation
    def next(self, fftinfo, is_multiprocessing=False):

        if not is_multiprocessing:
            self.svg.new_drawing()

        fitfourier = self.config["fourier"]["fitfourier"]

        fft = fftinfo["fft"]
        fft = [abs(x) for x in fft]
        fft = self.smooth(fft, fitfourier["fft_smoothing"])

        # fft = resampy.resample(fft, len(fft), len(fft)*fitfourier["tesselation"])

        if self.current_fft == None:
            self.current_fft = [0 for _ in range(len(fft))]

        interpolation = self.config["fourier"]["interpolation"]

        # Interpolate the next fft with the current one
        for index in range(len(self.current_fft)):
            self.current_fft[index] = interpolation["function"](
                self.current_fft[index],  
                fft[index],
                self.current_step,
                interpolation["steps"],
                self.current_fft[index],
                interpolation["arg_a"]
            )

        if not is_multiprocessing:

            fitted_fft = [0 for _ in range(len(fft))]

            for i in range(len(fft) - 1):
                
                transformed_index = int((len(fft) - 1) * (self.functions.proportion(len(fft) - 1, 1, i) ** 2))
                # transformed_index = int((len(fft) - 1) * (math.log(1 +self.functions.proportion(len(fft) - 1, 9, i), 10)))
                fitted_fft[i] = self.current_fft[transformed_index]

            fitted_fft = self.smooth(fitted_fft, fitfourier["fft_smoothing"])
            fitted_fft = resample(fitted_fft, len(fitted_fft), len(fitted_fft)*fitfourier["tesselation"])

            cut = [0.05, 0.95]
            fitted_fft = fitted_fft[
                int(len(fitted_fft)*cut[0])
                :
                int(len(fitted_fft)*cut[1])
            ]

            mode = self.config["mode"]

            if self.config["type"] == "circle":

                points = []
                
                # avg_fft = sum(fft)/len(fft)
                # fft = [max(x - avg_fft, 0) for x in fft]

                for i in range(len(fitted_fft) - 1):

                    size = fitted_fft[i]*(0.1 + i/80)

                    # Simple
                    if mode == "linear":
                        self.polar.from_r_theta(
                            self.config["minimum_bar_distance"] + size,
                            ((math.pi*2)/len(fitted_fft))*i # fitted_fft -> fft nice effect
                        )

                    # Symetric
                    if mode == "symetric":
                        self.polar.from_r_theta(
                            self.config["minimum_bar_distance"] + size,
                            (math.pi/2) - (((math.pi)/len(fitted_fft))*i) # fitted_fft -> fft nice effect
                        )
                    
                    coord = self.polar.get_rectangular_coordinates()
                    points.append(coord)

                if mode == "symetric":
                    for point in reversed(points):
                        points.append([ - point[0], point[1]])
                
                points.append(points[0])
                
                self.svg.dwg.add(
                    self.svg.dwg.polyline(
                        points,
                        stroke=svgwrite.rgb(60, 60, 60, '%'),
                        fill='white',
                    )
                )

                array = self.svg.get_array()
            self.current_step += 1

            return array
        self.current_step += 1

    # Blit this item on the canvas
    def blit(self, canvas):

        img = self.image
        width, height, _ = img.frame.shape
        
        x = int(self.x + self.offset[1] + self.base_offset[1])
        y = int(self.y + self.offset[0] + self.base_offset[0])

        canvas.canvas.overlay_transparent(
            self.image.frame,
            y,
            x
        )