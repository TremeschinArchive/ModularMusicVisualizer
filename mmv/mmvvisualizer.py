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

from mmv.coordinates import PolarCoordinates
from mmv.interpolation import Interpolation
from mmv.functions import FitTransformIndex
from mmv.functions import Functions
from resampy import resample
from mmv.modifiers import *
from mmv.frame import Frame
from mmv.utils import Utils
from mmv.svg import SVG
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
        self.svg = SVG(
            self.config["width"],
            self.config["height"],
            "cairo", #self.context.svg_rasterizer, # cairo is just faster here
            "png"
        )

        self.fit_transform_index = FitTransformIndex()
        self.functions = Functions()
        self.utils = Utils()

        self.path = {}

        self.x = 0
        self.y = 0
        self.size = 1
        self.current_animation = 0
        self.current_step = 0
        self.is_deletable = False
        self.offset = [0, 0]
        self.polar = PolarCoordinates()

        self.current_fft = {}

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

        ffts = fftinfo["fft"]

        # Abs of left and right channel
        ffts = [
            np.abs(ffts[0]),
            np.abs(ffts[1])
        ]

        # Add mean FFT, the "mid/mean" (m) channel
        ffts.append( (ffts[0] + ffts[1]) / 2 )

        # Smooth the ffts
        if fitfourier["pre_fft_smoothing"] > 0:
            ffts = [ self.smooth(fft, fitfourier["pre_fft_smoothing"]) for fft in ffts ]

        # The order of channels on the ffts list
        channels = ["l", "r", "m"]

        # The points to draw the visualization
        points = {}

        # Start each channel point's empty
        for channel in channels:
            points[channel] = []

        # Loop on each channel
        for channel_index, channel in enumerate(channels):

            # Get this channel raw fft and its size
            fft = ffts[channel_index]
            fft_size = fft.shape[0]
            
            # Create a empty zeros array as a starting point for the interpolation
            if not channel in list(self.current_fft.keys()):
                self.current_fft[channel] = np.zeros(fft_size)

            # The interpolation dictionary
            interpolation = self.config["fourier"]["interpolation"]

            # Interpolate the next fft with the current one
            for index in range(len(self.current_fft[channel])):
                self.current_fft[channel][index] = interpolation["function"](
                    self.current_fft[channel][index],  
                    fft[index],
                    self.current_step,
                    interpolation["steps"],
                    self.current_fft[channel][index],
                    interpolation["arg_a"]
                )

            # We calculate the points on a Worker process, main core loop stops at the ffts interpolation
            if not is_multiprocessing:
                
                # Start a zero fitted fft list
                fitted_fft = np.zeros(fft_size)
                fitted_fft = self.current_fft[channel]

                """
                # For each index starting from zero up until the FFT size
                for index in range(fft_size):
                    
                    # Fit the transformed index
                    exponent = 2.2
                    transformed_index_this = self.fit_transform_index.polynomial(index, fft_size, exponent)
                    transformed_index_next = self.fit_transform_index.polynomial(index + fft_size//100, fft_size, exponent)

                    this_index_fft_value = 0

                    if transformed_index_this == transformed_index_next:
                        this_index_fft_value = self.current_fft[channel][transformed_index_this]
                    else:
                        this_index_fft_value = np.mean(
                            self.current_fft[channel][
                                transformed_index_this:transformed_index_next
                            ]
                        )

                    # Get the transformed_index from the interpolated fft into the fitted fft linear indexing
                    fitted_fft[index] = this_index_fft_value
                """

                # Smooth the peaks
                if fitfourier["pos_fft_smoothing"] > 0:
                    fitted_fft = self.smooth(fitted_fft, fitfourier["pos_fft_smoothing"])

                # Apply "subdivision", break jagged edges into more smooth parts
                if fitfourier["subdivide"] > 0:
                    fitted_fft = resample(fitted_fft, fitted_fft.shape[0], fitted_fft.shape[0] * fitfourier["subdivide"])

                # Ignore the really low end of the FFT as well as the high end frequency spectrum
                cut = [0, 0.95]

                # Cut the fitted fft
                fitted_fft = fitted_fft[
                    int(fitted_fft.shape[0]*cut[0])
                    :
                    int(fitted_fft.shape[0]*cut[1])
                ]

                # The mode (linear, symetric)
                mode = self.config["mode"]

                # If we'll be making a circle 
                if self.config["type"] == "circle":

                    # For each item on the fitted FFT
                    for i in range(len(fitted_fft) - 1):

                        # Calculate our size of the bar
                        size = fitted_fft[i]*(2 + i/80) #- i/len(fitted_fft))

                        # Simple, linear
                        if mode == "linear":
                            # We only use the mid channel
                            if channel == "m":
                                self.polar.from_r_theta(
                                    (self.config["minimum_bar_size"] + size)*self.size,
                                    ((math.pi*2)/len(fitted_fft))*i # fitted_fft -> fft nice effect
                                )
                                coord = self.polar.get_rectangular_coordinates()
                                points[channel].append(coord)

                        # Symetric
                        if mode == "symetric":

                            angle = ( i/len(fitted_fft) ) * (math.pi)
                            angle = self.fit_transform_index.polynomial(angle, math.pi, 0.4)

                            bar_size = (self.config["minimum_bar_size"] + size)*self.size

                            # The left channel starts at the top and goes clockwise
                            if channel == "l":
                                self.polar.from_r_theta(
                                    bar_size,
                                    (math.pi/2) - angle, # fitted_fft -> fft nice effect
                                )
                                coord = self.polar.get_rectangular_coordinates()
                                points[channel].append(coord)

                            elif channel == "r":
                                self.polar.from_r_theta(
                                    bar_size,
                                    (math.pi/2) + angle # fitted_fft -> fft nice effect
                                )
                                coord = self.polar.get_rectangular_coordinates()
                                points[channel].append(coord)

        self.current_step += 1

        if not is_multiprocessing:

            drawpoints = []

            if mode == "symetric":
                for point in points["l"]:
                    drawpoints.append(point)
                for point in reversed(points["r"]):
                    drawpoints.append(point)
            
            if mode == "linear":
                for point in points["m"]:
                    drawpoints.append(point)

            drawpoints.append(drawpoints[0])
            
            self.svg.dwg.add(
                self.svg.dwg.polyline(
                    drawpoints,
                    stroke=svgwrite.rgb(60, 60, 60, '%'),
                    fill='white',
                )
            )

            array = self.svg.get_array()

            return array

    # Blit this item on the canvas
    def blit(self, canvas):

        x = int(self.x + self.offset[1] + self.base_offset[1])
        y = int(self.y + self.offset[0] + self.base_offset[0])

        canvas.canvas.overlay_transparent(
            self.image.frame, y, x
        )

