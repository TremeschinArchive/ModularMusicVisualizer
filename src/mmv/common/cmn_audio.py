"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Deal with converting, reading audio files and getting their info

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

from mmv.common.cmn_utils import DataUtils
from mmv.common.cmn_fourier import Fourier
import mmv.common.cmn_any_logger
from scipy.io import wavfile
import numpy as np
import subprocess
import samplerate
import librosa
import os


class AudioFile:

    # Read a .wav file from disk and gets the values on a list
    def read(self, path: str) -> None:

        debug_prefix = "[Audio.read]"

        print(debug_prefix, "Reading stereo audio")
        self.stereo_data, self.sample_rate = librosa.load(path, mono=False, sr=None)
        
        print(debug_prefix, "Calculating mono audio")
        self.mono_data = (self.stereo_data[0] + self.stereo_data[1]) / 2

        self.duration = self.stereo_data.shape[1] / self.sample_rate
        self.channels = self.stereo_data.shape[0]
        
        print(debug_prefix, f"Duration = [{self.duration:.2f}s]")


class AudioProcessing:
    def __init__(self) -> None:
        self.fourier = Fourier()
        self.datautils = DataUtils()
        self.config = None

    # Slice a mono and stereo audio data
    def slice_audio(self,
            stereo_data: np.ndarray,
            mono_data: np.ndarray,
            sample_rate: int,
            start_cut: int,
            end_cut: int,
            batch_size: int=None
        ) -> None:
        
        # Cut the left and right points range
        left_slice = stereo_data[0][start_cut:end_cut]
        right_slice = stereo_data[1][start_cut:end_cut]

        # Cut the mono points range
        mono_slice = mono_data[start_cut:end_cut]

        if not batch_size == None:
            # Empty audio slice array if we're at the end of the audio
            self.audio_slice = np.zeros([3, batch_size])

            # Get the audio slices of the left and right channel
            self.audio_slice[0][ 0:left_slice.shape[0] ] = left_slice
            self.audio_slice[1][ 0:right_slice.shape[0] ] = right_slice
            self.audio_slice[2][ 0:mono_slice.shape[0] ] = mono_slice

        else:
            self.audio_slice = [left_slice, right_slice, mono_slice]

        # Calculate average amplitude
        self.average_value = float(np.mean(np.abs(mono_slice)))

    def resample(self,
            data: np.ndarray,
            original_sample_rate: int,
            new_sample_rate: int
        ) -> None:

        ratio = new_sample_rate / original_sample_rate
        if ratio == 1:
            return data
        else:
            return samplerate.resample(data, ratio, 'sinc_best')

    # Get N semitones above / below A4 key, 440 Hz
    def get_frequency_of_key(self, n):
        return 440 * ( (2**(1/12)) ** n )

    # https://stackoverflow.com/a/2566508
    def find_nearest(self, array, value):
        index = (np.abs(array - value)).argmin()
        return index, array[index]
    
    # Calculate the FFT of this data, get only wanted frequencies based on the musical notes
    def process(self,
            data: np.ndarray,
            original_sample_rate: int
        ) -> None:
        
        # The returned dictionary
        processed = {}

        # Iterate on config
        for key, value in self.config.items():

            # Get info on config
            sample_rate = value.get("sample_rate")
            start_freq = value.get("start_freq")
            end_freq = value.get("end_freq")

            N = len(data)

            # Resample audio to target sample rate
            resampled = self.resample(data, original_sample_rate, sample_rate)

            # Get freqs vs fft value dictionary
            # binnedft_fft[0] -> freqs
            # binnedft_fft[1] -> values
            binned_fft = self.fourier.binned_fft(resampled, sample_rate)
            LENFFT = len(binned_fft[0])

            # All frequencies and the ones we want
            wanted_freqs = self.datautils.list_items_in_between(
                [self.get_frequency_of_key(x) for x in range(-100, 100)],
                start_freq,
                end_freq,
            )

            # Get the nearest freq and add to processed            
            for freq in wanted_freqs:
                # nearest[0] -> index (item)
                # nearest[1] -> index (value)
                nearest = self.find_nearest(binned_fft[0], freq)
                value = binned_fft[1][nearest[0]]
                processed[nearest[1]] = value
                
        linear_processed_fft = []
        frequencies = []

        for frequency, value in processed.items():
            frequencies.append(frequency)
            linear_processed_fft.append(value)
        
        return [linear_processed_fft, frequencies]