"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Apply fourier transformations on numpy array audio data based on
settings like sample size, return "binned frequencies" representation.

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

from scipy.fft import rfft, rfftfreq
import numpy as np
import math

class Fourier:

    # Calculate an Fast Fourier Transform, doesn't return DC bias (first bin)
    # and cuts up to the middle where the useful info ends
    def fft(self, data: np.ndarray) -> np.ndarray:
        # 1. Calculate the fft fft(data)
        # 2. Only need half the list of fft and don't need the DC bias (first item)
        #    - [1 : int(len(N) / 2)] = [1 : len(N) // 2]
        return rfft(data)

    # For more information, https://stackoverflow.com/questions/4364823
    #
    # This function accepts a data input, its samplerate and the "original sample rate" before
    # we downsample the data for getting better information of the FFT at lower frequencies.
    # We return a 2d array with pairs of
    #
    # > [[FFT freq], [FFT values]]
    #
    # Where each index of the FFT freq correspond to the other array's index FFT value
    #
    def binned_fft(self, data: np.ndarray, target_sample_rate: int, original_sample_rate: int = 48000) -> np.ndarray:

        # # Get the "normalized" FFT based on the sample rates

        # " The height is a reflection of power density, so if you double the sampling frequency,
        # and hence half the width of each frequency bin, you'll double the amplitude of the FFT result."
        # >> https://wiki.analytica.com/FFT
        #
        # 2^(new_sample_rate/original_sample_rate) = power gain
        # Divide by that but offset by 1 since if new fs = old fs we multiply by 1/2^0 = 1
        #
        raw_fft = self.fft(data) * (2 ** math.log2(original_sample_rate / target_sample_rate))
        # raw_fft = self.fft(data)

        # # TODO: wont work for old fs and new fs equal
        # if original_sample_rate != target_sample_rate:
        #     raw_fft *= (math.log10(original_sample_rate / target_sample_rate) / math.log10(2))

        # # Get the frequencies that FFT represent based on the sample rate

        # Get the frequencies that the indexes determine
        fftf = rfftfreq(raw_fft.shape[0], 1 / target_sample_rate)

        # # Return pairs of [[freq], [fft]] array
        return np.array([fftf, raw_fft], dtype = object)
