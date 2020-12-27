"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
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

from scipy.fftpack import fft
import numpy as np
import math


class Fourier:

    # Calculate an Fast Fourier Transform, doesn't return DC bias (first bin)
    # and cuts up to the middle where the useful info ends
    def fft(self, data: np.ndarray) -> np.ndarray:

        # 1. Calculate the fft fft(data)
        # 2. Only need half the list of fft and don't need the DC bias (first item)
        #    - [1 : int(len(N) / 2)] = [1 : len(N) // 2]
        return fft(data)[1:len(data) // 2]
    
    # For more information, https://stackoverflow.com/questions/4364823
    #
    # This function accepts a data input, its samplerate and the "original sample rate" before
    # we downsample the data for getting better information of the FFT at lower frequencies.
    # We return a single array with the following strucutre:
    #
    # > [[FFT_freq_1, FFT_value_1], [FFT_freq_3, FFT_value_2], ...]
    #
    def binned_fft(self, data: np.ndarray, sample_rate: int, original_sample_rate: int = 48000) -> list:

        # # Get the "normalized" fft based on the sample rates

        # " The height is a reflection of power density, so if you double the sampling frequency,
        # and hence half the width of each frequency bin, you'll double the amplitude of the FFT result.""
        # >> https://wiki.analytica.com/FFT
        #
        # sample_rate * 2^n = original_sample_rate
        # 2^n = original_sample_rate / sample_rate
        # n log(2) = log(sample_rate / original_sample_rate)
        # n = log(sample_rate / original_sample_rate) / log(2)
        # where sample_rate / original_sample_rate = ratio
        #
        # We use log10 cause it's faster than ln, on my pc:
        # 
        #   >>> s = time.time(); b = [math.log(x) for x in range(1, 10000000)]; time.time() - s
        #   2.073245048522949
        #   >>> s = time.time(); b = [math.log10(x) for x in range(1, 10000000)]; time.time() - s
        #   1.3057165145874023
        #
        # The expression would be the following:
        #
        fft = self.fft(data) * (math.log10(original_sample_rate / sample_rate) / math.log10(2))
        # 
        # We could use the following log law to simplify it:
        #
        # $$ \log_b (a) = \frac{\log_{10} (a)}{\log_{10} (b)} $$
        #
        # So we end up calculating the log_2 (ratio)
        #
        # fft = self.fft(data) * (math.log(original_sample_rate / sample_rate, 2))
        #
        # .. But Python math's module is more optimized for finding the log10 and
        # calculating 2 logs then dividing ends up faster than a custom base log.
        # The log2 above is about the intuition of it I guess..
        #

        # # Get the frequencies that FFT represent based on the sample rate

        # Get the frequencies that the indexes determine
        fftf = np.fft.fftfreq(len(data), 1 / sample_rate)

        # Only need the first half of frequencies cause imaginary mirroring
        fftf = fftf[1 : len(fftf) // 2]

        # # Return pairs of [freq, fft]

        # We return a single array with pairs of ffreq and fft
        # So we do a vertical stack, that is:
        #
        # a = [1, 2, 3, 4, 5]
        # b = [6, 7, 8, 9, 0]
        #
        # c = np.vstack(a, b) -> 
        #       [[1, 2, 3, 4, 5],
        #        [6, 7, 8, 9, 0]]
        # 
        # Then  we transpose it, that is, flip it 90° clockwise then
        # mirror vertically so we end up with the pairs:
        #
        # c.T ->
        #   [[1, 6],
        #    [2, 7],
        #    [3, 8],
        #    [4, 9],
        #    [5, 0]]
        #
        # Which is what our specification says and what we need.
        #
        # Note that the first array is the index 0 of each vector
        # so we represent it with th eFFT frequencies and that's why
        # we put fftf first than fft, actually it is already explicitly
        # in the order we want.
        #
        return np.vstack((fftf, fft)).T
