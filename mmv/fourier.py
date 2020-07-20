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
import numpy as np


class Fourier():

    # Calculate an Fast Fourier Transform, doesn't return DC bias (first bin)
    # and cuts up to the middle where the useful info ends
    def fft(self, data):

        debug_prefix = "[Fourier.fft]"

        # Normalize the data on [-1, 1]
        normalize_scalar = np.linalg.norm(data)

        # If the array is only zeros then normalize_scalar is zero
        # We can't divide by zero so..
        if normalize_scalar > 0:
            normalized = normalized / normalize_scalar
        else:
            normalized = data

        # Calculate the fft
        # print(debug_prefix, "Calculating FFT")
        transform = fft(normalized)

        # Only need half the list of fft and don't need the DC bias (first item)
        cut = [1, len(normalized) // 2]

        return transform[cut[0]:cut[1]]

    # For more information, https://stackoverflow.com/questions/4364823
    def binned_fft(self, data, sample_rate):
        
        # The FFT length
        N = data.shape[0]

        # Get the nth frequency of the fft
        get_bin = lambda n : n * (sample_rate/N)

        # Get the fft
        fft = self.fft(data)

        bined_fft = {}

        # Assign freq vs fft on a dictionary
        for index in range(1, N):
            binned_fft[get_bin(index)] = fft[index]   

        return binned_ffet