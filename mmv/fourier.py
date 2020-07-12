"""
===============================================================================

Purpose: Apply fourier transformations on numpy array audio data based on
settings like sample size

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

from scipy.fftpack import fft
from scipy import arange
import numpy as np


class Fourier():
    def fft(self, data, info):

        debug_prefix = "[Fourier.fft]"

        # Normalize the data on [-1, 1] based on the bit count
        # print(debug_prefix, "Normalizing the data")
        normalized = [(x/2**info["bit_depth"])*2 - 1 for x in data]

        # Calculate the fft
        # print(debug_prefix, "Calculating FFT")
        transform = fft(normalized)

        # print(debug_prefix, "len(data) =", len(data))
        # print(debug_prefix, "len(fft) =", len(transform))

        # Only need half the list of fft
        cut = [
            2, int(len(normalized)/2) - 200
        ]

        return transform[cut[0]:cut[1]]


class FitFourier():
    def polynomial(self, fft, exponent):
        pass
