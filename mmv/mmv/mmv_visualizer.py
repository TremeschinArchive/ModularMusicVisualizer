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


from mmv.mmv_visualizers.mmv_visualizer_circle import MMVVisualizerCircle
from mmv.common.cmn_coordinates import PolarCoordinates
from mmv.common.cmn_interpolation import Interpolation
from mmv.common.cmn_functions import Functions
from mmv.common.cmn_functions import FitIndex
from mmv.common.cmn_skia import SkiaWrapper
from mmv.common.cmn_frame import Frame
from mmv.common.cmn_utils import Utils
from mmv.mmv_modifiers import *
from resampy import resample
import svgwrite
import random
import math
import os

import numpy as np

class MMVVisualizer:
    def __init__(self, context, config: dict, skia_object) -> None:
        
        debug_prefix = "[MMVVisualizer.__init__]"
        
        self.context = context
        self.config = config
        self.skia = skia_object

        self.fit_transform_index = FitIndex()
        self.functions = Functions()
        self.utils = Utils()

        self.path = {}

        self.x = 0
        self.y = 0
        self.size = 1
        self.is_deletable = False
        self.offset = [0, 0]
        self.polar = PolarCoordinates()

        self.current_fft = {}

        # Create Frame and load random particle
        self.image = Frame()

        if self.config["type"] == "circle":
            self.builder = MMVVisualizerCircle(self, self.skia)

    def smooth(self, array, smooth):
        if smooth > 0:
            box = np.ones(smooth)/smooth
            array_smooth = np.convolve(array, box, mode='same')
            return array_smooth
        return array

    # Next step of animation
    def next(self, fftinfo, effects, is_multiprocessing=False):

        self.skia.reset_canvas()

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
        ffts = [ self.smooth(fft, fitfourier["pre_fft_smoothing"]) for fft in ffts ]

        # The order of channels on the ffts list
        channels = ["l", "r", "m"]

        # The points to draw the visualization
        points = {}

        # Start each channel point's empty
        for channel in channels:
            points[channel] = []

        # Dictionary with all the data to make a visualization bar
        fitted_ffts = {}

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
                
                interpolation.start_value = self.current_fft[channel][index]
                interpolation.target_value = fft[index]
                interpolation.current_value = self.current_fft[channel][index]

                self.current_fft[channel][index] = interpolation.next()


            # We calculate the points on a Worker process, main core loop stops at the ffts interpolation
            if not is_multiprocessing:
                
                # Start a zero fitted fft list
                fitted_fft = np.copy( self.current_fft[channel] )

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

                fitted_ffts[channel] = np.copy(fitted_fft)

        return self.builder.build(fitted_ffts, self.config, effects)

        """ 
                # If we'll be making a circle 
                if self.config["type"] == "circle":

                    # For each item on the fitted FFT
                    for i in range(len(fitted_fft) - 1):

                        # Calculate our size of the bar
                        size = fitted_fft[i]*8 #*(0.7 + i/80) #- i/len(fitted_fft))

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
                """
        """ 
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

            png = self.svg.get_png()

            return png """

    # Blit this item on the canvas
    def blit(self, canvas):

        x = int(self.x + self.offset[1] + self.base_offset[1])
        y = int(self.y + self.offset[0] + self.base_offset[0])

        canvas.canvas.overlay_transparent(
            self.image.array, y, x
        )

