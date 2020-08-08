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

from mmv.common.cmn_coordinates import PolarCoordinates
import numpy as np
import math
import skia


class MMVVisualizerCircle:
    def __init__(self, MMVVisualizer, skia_object):
        self.visualizer = MMVVisualizer
        self.skia = skia_object
        self.config = self.visualizer.config
        self.polar = PolarCoordinates()

        self.center_x = self.visualizer.context.width / 2
        self.center_y = self.visualizer.context.height / 2

    def build(self, fitted_ffts: dict, config, effects) -> np.ndarray:

        if self.config["mode"] == "symetric":
            
            for channel in ["l", "r"]:

                this_channel_fft = fitted_ffts[channel]
                npts = len(this_channel_fft)

                for index, magnitude in enumerate(this_channel_fft):

                    paint = skia.Paint(
                        AntiAlias = True,
                        Color = skia.Color4f(1, 1, 1, 1),
                        Style = skia.Paint.kStroke_Style,
                        StrokeWidth = 1,
                    )

                    path = skia.Path()
                    path.moveTo(self.center_x, self.center_y)
                    
                    if channel == "l":
                        theta = (math.pi/2) - ((index/npts)*math.pi)
                    elif channel == "r":
                        theta = (math.pi/2) + ((index/npts)*math.pi)

                    self.polar.from_r_theta(
                        r = ( self.config["minimum_bar_size"] + magnitude * 5 ) * effects["size"],
                        theta = theta,
                    )

                    polar_offset = self.polar.get_rectangular_coordinates()

                    path.lineTo(
                        self.center_x + polar_offset[0],
                        self.center_y + polar_offset[1],
                    )

                    self.skia.canvas.drawPath(path, paint)

