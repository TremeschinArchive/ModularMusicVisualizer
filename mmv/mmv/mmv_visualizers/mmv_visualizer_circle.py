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

import numpy as np
import skia


class MMVVisualizerCircle:
    def __init__(self, MMVVisualizer, skia_object):
        self.visualizer = MMVVisualizer
        self.skia = skia_object
        self.config = self.visualizer.config

    def build(self, fitted_ffts: dict, config, effects) -> np.ndarray:

        paint = skia.Paint(
            AntiAlias=True,
            Color=skia.ColorWHITE,
            Style=skia.Paint.kFill_Style,
            StrokeWidth=4,
        )

        if self.config["mode"] == "symetric":
            
            self.skia.canvas.translate(self.skia.context.width / 2, self.skia.context.height / 2)
            self.skia.canvas.rotate(90)

            for channel in ["l", "r"]:

                this_channel_fft = fitted_ffts[channel]
                npts = len(this_channel_fft)

                for index, magnitude in enumerate(this_channel_fft):
                    rect = skia.Rect(
                        0,
                        -1, #* effects["size"] , 
                        ( self.config["minimum_bar_size"] + magnitude*5 ) * effects["size"],
                        1) #* effects["size"])
                    self.skia.canvas.drawRect(rect, paint)

                    if channel == "l":
                        self.skia.canvas.rotate(180/npts)
                    elif channel == "r":
                        self.skia.canvas.rotate( - 180/npts)
                
                if channel == "l":
                    self.skia.canvas.rotate(180)
            
            self.skia.canvas.rotate(90)

            self.skia.canvas.translate( - self.skia.context.width / 2, - self.skia.context.height / 2)
            