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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
from mmv.common.cmn_functions import Functions
from mmv.common.cmn_utils import DataUtils
from mmv.common.cmn_fourier import Fourier
import mmv.common.cmn_any_logger
import audio2numpy
import numpy as np
import subprocess
import samplerate
import soundfile
import audioread
import logging
import math
import os


class AudioFile:

    # Read a .wav file from disk and gets the values on a list
    def read(self, path: str, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[AudioFile.read]"
        ndepth = depth + LOG_NEXT_DEPTH

        logging.info(f"{depth}{debug_prefix} Reading stereo audio in path [{path}], trying soundfile")
        try:
            self.stereo_data, self.sample_rate = soundfile.read(path)
        except RuntimeError:
            logging.warn(f"{depth}{debug_prefix} Couldn't read file with soundfile, trying audio2numpy..")
            self.stereo_data, self.sample_rate = audio2numpy.open_audio(path)

        # We need to transpose to a (2, -1) array
        logging.info(f"{depth}{debug_prefix} Transposing audio data")
        self.stereo_data = self.stereo_data.T

        # Calculate the duration and see how much channels this audio file have
        self.duration = self.stereo_data.shape[1] / self.sample_rate
        self.channels = self.stereo_data.shape[0]
        
        # Log few info on the audio file
        logging.info(f"{depth}{debug_prefix} Duration of the audio file = [{self.duration:.2f}s]")
        logging.info(f"{depth}{debug_prefix} Audio sample rate is         [{self.sample_rate}]")
        logging.info(f"{depth}{debug_prefix} Audio data shape is          [{self.stereo_data.shape}]")
        logging.info(f"{depth}{debug_prefix} Audio have                   [{self.channels}]")

        # Get the mono data of the audio
        logging.info(f"{depth}{debug_prefix} Calculating mono audio")
        self.mono_data = (self.stereo_data[0] + self.stereo_data[1]) / 2

        # Just make sure the mono data is right..
        logging.info(f"{depth}{debug_prefix} Mono data shape:             [{self.mono_data.shape}]")

class AudioProcessing:
    def __init__(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[AudioProcessing.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH

        self.fourier = Fourier()
        self.datautils = DataUtils()
        self.functions = Functions()
        self.config = None

        # MMV specific, where we return repeated frequencies from the
        # function process
        self.where_decay_less_than_one = 440
        self.value_at_zero = 5

        # List of full frequencies of notes
        # - 50 to 68 yields freqs of 24.4 Hz up to 
        self.piano_keys_frequencies = [round(self.get_frequency_of_key(x), 2) for x in range(-50, 68)]
        logging.info(f"{depth}{debug_prefix} Whole notes frequencies we'll care: [{self.piano_keys_frequencies}]")

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
        # mono_slice = mono_data[start_cut:end_cut]

        if not batch_size == None:
            # Empty audio slice array if we're at the end of the audio
            self.audio_slice = np.zeros([3, batch_size])

            # Get the audio slices of the left and right channel
            self.audio_slice[0][ 0:left_slice.shape[0] ] = left_slice
            self.audio_slice[1][ 0:right_slice.shape[0] ] = right_slice
            # self.audio_slice[2][ 0:mono_slice.shape[0] ] = mono_slice

        else:
            # self.audio_slice = [left_slice, right_slice, mono_slice]
            self.audio_slice = [left_slice, right_slice]

        # Calculate average amplitude
        self.average_value = float(np.mean(np.abs(
            mono_data[start_cut:end_cut]
        )))

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
    #
    # get_frequency_of_key(-12) = 220 Hz
    # get_frequency_of_key(  0) = 440 Hz
    # get_frequency_of_key( 12) = 880 Hz
    #
    def get_frequency_of_key(self, n):
        return 440 * (2**(n/12))

    # https://stackoverflow.com/a/2566508
    def find_nearest(self, array, value):
        index = (np.abs(array - value)).argmin()
        return index, array[index]
    
    # Calculate the FFT of this data, get only wanted frequencies based on the musical notes
    def process(self,
            data: np.ndarray,
            original_sample_rate: int,
        ) -> None:
        
        # The returned dictionary
        processed = {}

        # Iterate on config
        for _, value in self.config.items():

            # Get info on config
            sample_rate = value.get("sample_rate")
            start_freq = value.get("start_freq")
            end_freq = value.get("end_freq")

            # Get the frequencies we want and will return in the end
            wanted_freqs = self.datautils.list_items_in_between(
                self.piano_keys_frequencies,
                start_freq, end_freq,
            )

            # Calculate the binned FFT, we get N vectors of [freq, value]
            # of this FFT
            binned_fft = self.fourier.binned_fft(
                # Resample our data to the one specified on the config
                data = self.resample(
                    data = data,
                    original_sample_rate = original_sample_rate,
                    new_sample_rate = sample_rate,
                ),
                # # # # # # # # # # # # # # # # # # # # # # # # # # # #
                sample_rate =  sample_rate,
                original_sample_rate = original_sample_rate,
            )

            # Get the nearest freq and add to processed            
            for freq in wanted_freqs:

                # Get the nearest and FFT value
                nearest = self.find_nearest(binned_fft[0], freq)
                value = binned_fft[1][nearest[0]]
     
                # How much bars we'll render duped at this freq, see
                # this function on the Functions class for more detail
                N = math.ceil(
                    self.functions.how_much_bars_on_this_frequency(
                        x = freq,
                        where_decay_less_than_one = self.where_decay_less_than_one,
                        value_at_zero = self.value_at_zero,
                    )
                )

                # Add repeated bars or just one
                for i in range(N):
                    processed[nearest[1] + (i/10)] = value
                
        linear_processed_fft = []
        frequencies = []

        for frequency, value in processed.items():
            frequencies.append(frequency)
            linear_processed_fft.append(value)
        
        return [linear_processed_fft, frequencies]