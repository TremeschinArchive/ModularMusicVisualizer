"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

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
import math


class Fourier:

    # Calculate an Fast Fourier Transform, doesn't return DC bias (first bin)
    # and cuts up to the middle where the useful info ends
    def fft(self, data: np.ndarray) -> np.ndarray:

        # Calculate the fft
        transform = fft(data)

        # Only need half the list of fft and don't need the DC bias (first item)
        cut = [1, len(data) // 2]

        return transform[cut[0]:cut[1]]
    
    # " The height is a reflection of power density, so if you double the sampling frequency,
    # and hence half the width of each frequency bin, you'll double the amplitude of the FFT result.""
    # >> https://wiki.analytica.com/FFT
    #
    # sample_rate * 2^n = original_sample_rate
    # 2^n = original_sample_rate / sample_rate
    # n log(2) = log(sample_rate / original_sample_rate)
    # n = log(sample_rate / original_sample_rate) / log(2)
    # where sample_rate / original_sample_rate = ratio
    def get_normalizer_scalar(self, ratio: float) -> float:
        return math.log10(ratio) / math.log10(2)

    # For more information, https://stackoverflow.com/questions/4364823
    def binned_fft(self, data: np.ndarray, sample_rate: int, original_sample_rate: int = 48000) -> list:
        
        # Get the norm scalar
        norm = self.get_normalizer_scalar(original_sample_rate / sample_rate)

        # Get the normalized fft
        fft = self.fft(data)*norm

        # Get the frequencies that the indexes determine
        fftf = np.fft.fftfreq(len(data), 1/sample_rate)

        # Only need the first half of frequencies cause imaginary mirroring
        fftf = fftf[1:len(fftf) // 2]

        # Return the arrays
        return fftf, fft
