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

from mmv.common.cmn_skia import SkiaWrapper
import numpy as np
import skia


class MMVVisualizerCircle:
    def __init__(self, MMVVisualizer):
        self.visualizer = MMVVisualizer
        self.config = self.visualizer.config

    def build(self, fitted_ffts: dict, blit_to) -> np.ndarray:
        print(fitted_ffts)
        npts = len(fitted_ffts.keys())

        paint = skia.Paint(
            AntiAlias=True,
            Color=skia.ColorBLUE,
            Style=skia.Paint.kFill_Style,
            StrokeWidth=4,
        )

        with self.skia.surface as canvas:
            if self.config["mode"] == "symetric":

                rect = skia.Rect(0, -5, fitted_ffts, 5)
                canvas.drawRect(rect, paint)
                canvas.rotate((360/npts)/2)
                
