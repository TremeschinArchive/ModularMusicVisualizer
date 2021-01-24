"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVSkiaMusicBars object for music bars

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

from mmv.mmvskia.music_bars.mmv_skia_music_bar_circle import MMVSkiaMusicBarsCircle
from mmv.common.cmn_coordinates import PolarCoordinates
from mmv.common.cmn_interpolation import Interpolation
from mmv.common.cmn_functions import Functions
from mmv.mmvskia.mmv_skia_modifiers import *
from mmv.common.cmn_frame import Frame
from mmv.common.cmn_utils import Utils
import numpy as np
import random
import math
import os



class MMVSkiaMusicBarsVectorial:
    """
    config:
    {
        "type": str, what class we are:
            "circle": MMVSkiaMusicBarsCircle

        For MMVSkiaMusicBarsCircle: {
            "minimum_bar_size": float
                Starting radius of the bars
            "maximum_bar_size": float, math.inf if not set
                Hard crop biased by minimum bar size, ie. minimum = 200, maximum = 100 bar will only reach 300
            "center_x" // "center_y": int, str, "center"
                Center point of the radial music bars
                If set to "center", sets to half the Context.width for center_x and half the Context.height to center_y
            "fft_20hz_multiplier", "fft_20khz_multiplier": float
                Explained on mmv_skia_music_bar_circle.py
            "bar_magnitude_multiplier": float, 1
                Multiply the default magnitude of bars relative to the FFT by this much
            "bigger_bars_on_magnitude": bool, True
                Increase stroke width of the bars based on the magnitude
            "bigger_bars_on_magnitude_add_magnitude_divided_by: float, 64
                If bigger_bars_on_magnitude is True, add to the stroke width the FFT magnitude divided by this
            "bar_starts_from": str, "center"
                "center": Bars starts from center and grows to its point in radial direction
                "last": Bars start from last bar end position, a somewhat halo around the logo

            # Colors
            
            "color_preset": str, "colorful"
                - "colorful": radial colors
                    - "color_rotates": bool, True
                        ach step add a value to shift the colors
                    - "color_rotate_speed": int, 100
                        More is slower, adds step/color_rotate_speed radians
        }
    }
    """
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv
        
        debug_prefix = "[MMVSkiaMusicBars.__init__]"
        
        self.kwargs = kwargs

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

        self.image = Frame()

        # Configuration

        self.kwargs["fourier"] = {
            "interpolation": MMVSkiaInterpolation(
                self.mmv,
                function = "remaining_approach",
                ratio = self.kwargs.get("bar_responsiveness", 0.25),
            ),
        }

        # # We use separate file and classes for each type of visualizer

        # Circle, radial visualizer
        if self.kwargs["type"] == "circle":
            self.builder = MMVSkiaMusicBarsCircle(self.mmv, self, **self.kwargs)

    # # Next methods

    # Next step of animation
    # This effects dictionary is about our MMVModifiers like Size, rotation or other skia filters we apply
    def next(self, effects):

        # # # We start with a bunch of routines for interpolating our fft on the three channels
        # # # according to the last value

        # Get info
        # fitfourier = self.kwargs["fourier"]["fitfourier"]
        frequencies = self.mmv.core.modulators["frequencies"]
        ffts = self.mmv.core.modulators["fft"]

        # Abs of left and right channel
        ffts = [
            np.abs(ffts[0]),
            np.abs(ffts[1])
        ]

        # Add mean FFT, the "mid/mean" (m) channel
        ffts.append( (ffts[0] + ffts[1]) / 2 )

        # The order of channels on the ffts list
        channels = ["l", "r"]

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
            interpolation = self.kwargs["fourier"]["interpolation"]

            # Interpolate the next fft with the current one
            for index in range(len(self.current_fft[channel])):
                
                # Set the corresponding start, target and current value
                interpolation.start_value = self.current_fft[channel][index]
                interpolation.target_value = fft[index]
                interpolation.current_value = self.current_fft[channel][index]

                # Get next value of the FFT
                self.current_fft[channel][index] = interpolation.next()

            # Start a zero fitted fft list
            fitted_fft = np.copy( self.current_fft[channel] )

            # Send the fitted fft to its list
            fitted_ffts[channel] = np.copy(fitted_fft)

        # Call our actual visualizer for drawing directly on the canvas
        self.builder.build(fitted_ffts, frequencies, self.kwargs, effects)
  