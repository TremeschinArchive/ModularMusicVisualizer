"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
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

from mmv.common.cmn_functions import Functions
from mmv.common.cmn_utils import DataUtils
from mmv.common.cmn_fourier import Fourier
import mmv.common.cmn_any_logger
from tqdm import tqdm
import audio2numpy
import numpy as np
import samplerate
import subprocess
import audioread
import soundfile
import threading
import logging
import math
import time
import os


# Read audio from a path
class AudioSourceFile:
    def __init__(self, ffmpeg_wrapper):
        self.ffmpeg_wrapper = ffmpeg_wrapper
        self.return_next_info_index = 0
        self.audio_processing = AudioProcessing()
        self.info = {}

    def configure(self, target_fps = 60, process_batch_size = 8096, sample_rate = 48000, do_calculate_fft = True):
        self.process_batch_size = process_batch_size
        self.current_batch = np.zeros((2, process_batch_size), dtype = np.float32)
        self.read_batch_size = int(sample_rate / target_fps)
        self.sample_rate = sample_rate
        self.do_calculate_fft = do_calculate_fft

    # Read a .wav file from disk and gets the values on a list
    def init(self, audio_path: str) -> None:
        debug_prefix = "[AudioSourceFile.init]"
        self.audio_path = audio_path

        logging.info(f"{debug_prefix} Reading total steps of audio in path [{audio_path}], can take a bit..")

        # Calculate total steps
        self.total_steps = 0
        for _ in self.read_progressive():
            self.total_steps += 1
        logging.info(f"{debug_prefix} Total steps: [{self.total_steps}]")

        self.duration = (self.total_steps * self.read_batch_size) / self.sample_rate
        logging.info(f"{debug_prefix} Duration: [{self.duration}]")

    # Progressively read the audio file in chunks so we don't assassinate the computer's memory in large files
    def read_progressive(self):
        for batch in self.ffmpeg_wrapper.raw_audio_from_file(
                input_file = self.audio_path, batch_size = self.read_batch_size,
                sample_rate = self.sample_rate, channels = 2):
            yield batch

    # Start a thread to process the audio
    def start(self):
        self.slice_process_thread = threading.Thread(target = self.__slice_process, daemon = True)
        self.slice_process_thread.start()

    def next(self, step):
        while not step + 1 in self.info.keys():
            time.sleep(0.01)
        
    def get_info(self):
        self.return_next_info_index += 1
        return self.info[self.return_next_info_index].copy()

    def __slice_process(self):
        assign_step_counter = 0

        # Progress bar
        progress_bar = tqdm(
            total = self.total_steps,
            unit = " slices",
            # unit_scale = True,
            dynamic_ncols = True,
            colour = '#00ff00',
            position = 1,
            smoothing = 0.3
        )

        # Arrange message such that both tqdm message align
        message = f"Processing Audio File"

        # Set the description
        progress_bar.set_description(message)

        for batch in self.read_progressive():
            len_batch = batch.shape[1]
            progress_bar.update(1)

            self.info[assign_step_counter] = {}

            # Insert new data
            for channel_number in [0, 1]:
                self.current_batch[channel_number] = np.roll(self.current_batch[channel_number], - len_batch, axis = -1)
                np.put(
                    # Target array
                    self.current_batch[channel_number], 

                    # Where on target array to put the data and input data
                    range(self.process_batch_size - len_batch, self.process_batch_size), batch[channel_number],         
                    mode = "wrap"  # Mode (wrap)
                )

            # This yields information as it was calculated so we assign the key (index 0) to the value (index 1)
            for info in self.audio_processing.get_info_on_audio_slice(
                audio_slice = self.current_batch,
                original_sample_rate = self.sample_rate,
                do_calculate_fft = self.do_calculate_fft,
            ):
                self.info[assign_step_counter][info[0]] = info[1]
            assign_step_counter += 1
    

class AudioSourceRealtime:
    def __init__(self):
        self.audio_processing = AudioProcessing()

    def configure(self, batch_size = 8096, sample_rate = 48000, recorder_numframes = 256, do_calculate_fft = True):
        self.batch_size = batch_size
        self.current_batch = np.zeros((2, batch_size), dtype = np.float32)
        self.sample_rate = sample_rate
        self.recorder_numframes = recorder_numframes
        self.do_calculate_fft = do_calculate_fft

    def init(self, recorder_device = None, search_for_loopback = False):
        import soundcard
        debug_prefix = "[AudioSourceRealtime.init]"

        # Search for the first loopback device (monitor of the current audio output)
        # Probably will fail on Linux if not using PulseAudio but oh well
        if (search_for_loopback) and (recorder_device is None):
            logging.info(f"{debug_prefix} Attempting to find the first loopback device for recording")

            # Iterate on every "microphone", or recorder-capable devices to be more precise
            for device in soundcard.all_microphones(include_loopback = True):

                # If it's marked as loopback then we'll use it
                if device.isloopback:
                    self.recorder = device
                    logging.info(f"{debug_prefix} Found loopback device: [{device}]")
                    break            

            # If we didn't match anyone then recorder_device will be None and we'll error out soon
        else:
            # Assign the recorder given by the user since 
            self.recorder = recorder_device

        # Recorder device should not be none
        assert (self.recorder is not None), "Auto search is off and didn't give a target recorder device"

    def start(self): pass

    # Start the main routines since we configured everything
    def start_async(self):
        debug_prefix = "[AudioSourceRealtime.start_async]"
    
        logging.info(f"{debug_prefix} Starting the main capture and processing thread..")

        # Start the thread we capture and process the audio
        self.capture_process_thread = threading.Thread(target = self.capture_and_process_loop, daemon = True)
        self.capture_process_thread.start()

        # Wait until we have some info so we don't accidentally crash with None type has no attribute blabla
        self.info = {}
        while not self.info == {}:
            time.sleep(0.016)
    
    # Stop the main thread
    def stop(self):
        self.__should_stop = True
        self.__capture_threadshould_stop = True

    def __capture_thread_func(self):

        # Hard debug
        self.plot_audio = False
        if self.plot_audio:
            import matplotlib.pyplot as plt
            plt.ion()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            x = np.arange(self.batch_size)
            line1, = ax.plot(x, np.linspace(-0.2, 0.2, self.batch_size), 'b-')

        # Open a recorder microphone otherwise we open and close the stream on each loop
        with self.recorder.recorder(samplerate = self.sample_rate, channels = 2) as source:
            while not self.__capture_threadshould_stop:

                # The array with new stereo data to process, we get whatever there is ready that was
                # buffered (numframes = None) so we don't have to sync with the video or block the code
                # (though we're supposed to be multithreaded here so it won't matter but we lose the
                # ability to have big batch sizes in a "progressive" processing mode).
                # We also transpose the result so we get a [channels, samples] array shape
                new_audio_data = source.record(numframes = self.recorder_numframes).T

                # The number of new samples we got
                new_audio_data_len = new_audio_data.shape[1]

                # Offset the Left and Right arrays on the current batch itself by the length of the
                # new data, this is so we always use the last index as the next new and unread value
                # relative to when we keep adding and wrapping around, older data are near index 0
                self.current_batch = np.roll(self.current_batch, - new_audio_data_len, axis = -1)

                # Assign the new data to the current batch arrays
                for channel_number in [0, 1]:

                    # We simply np.put the new data on the current batch array with its entirety
                    # of the length (0, new_audio_data_len) on the mode to wrap the values around
                    # but since audio goes from negative x to positive x axis (vec2(1, 0) direction)
                    # we have to add it at the end
                    np.put(
                        self.current_batch[channel_number],                            # Target array
                        range(self.batch_size - new_audio_data_len, self.batch_size),  # Where on target array to put the data
                        new_audio_data[channel_number],                                # Input data
                        mode = "wrap"                                                  # Mode (wrap)
                    )
                        
                # Hard debug
                if self.plot_audio:
                    line1.set_ydata(self.current_batch[0])
                    fig.canvas.draw()

            self.__capture_threadshould_stop = False

    # This is the thread we capture the audio and process it, it's a bit more complicated than a 
    # class that reads from a file because we don't have guaranteed slices we read and also to 
    # synchronize the processing part and the frames we're rendering so it's better to just do
    # stuff as fast as possible here and get whatever next numframes we have to read 
    def capture_and_process_loop(self):

        # Thread and code flow control
        self.__capture_threadshould_stop = False
        self.__should_stop = False

        # A float32 zeros to store the current audio to process
        self.current_batch = np.zeros((2, self.batch_size), dtype = np.float32)
        self.info = {}

        self.__capture_thread = threading.Thread(target = self.__capture_thread_func, daemon = True)
        self.__capture_thread.start()

        # Until the user don't run the function stop
        while not self.__should_stop:
            
            # This yields information as it was calculated so we assign the key (index 0) to the value (index 1)
            for info in self.audio_processing.get_info_on_audio_slice(
                audio_slice = self.current_batch,
                original_sample_rate = self.sample_rate,
                do_calculate_fft = self.do_calculate_fft,
            ):
                self.info[info[0]] = info[1]
                if self.__should_stop: break
              
        self.__should_stop = False

    # Do nothing, we're threaded processing the audio
    def next(self, step):
        pass
    
    # We just return the current info
    def get_info(self):
        return self.info.copy()


class AudioProcessing:
    def __init__(self) -> None:
        debug_prefix = "[AudioProcessing.__init__]"

        # Create some util classes
        self.fourier = Fourier()
        self.datautils = DataUtils()
        self.functions = Functions()
        self.config = None

        # List of full frequencies of notes
        # - 50 to 68 yields freqs of 24.4 Hz up to 
        self.piano_keys_frequencies = [round(self.get_frequency_of_key(x), 2) for x in range(-50, 68)]

    # Get specs on config dictionary
    def _get_config_stuff(self, config_dict):

        # Get config
        start_freq = config_dict["start_freq"]
        end_freq = config_dict["end_freq"]

        # Get the frequencies we want and will return in the end
        wanted_freqs = self.datautils.list_items_in_between(
            self.piano_keys_frequencies,
            start_freq, end_freq,
        )

        # Counter for expected frequencies on this config
        expected_N_frequencies = 0
        expected_frequencies = []

        # Add target freq if it's not on the list
        for freq in wanted_freqs:

            # How much bars we'll render duped at this freq, see
            # this function on the Functions class for more detail
            N = math.ceil(
                self.functions.how_much_bars_on_this_frequency(
                    x = freq,
                    where_decay_less_than_one = self.where_decay_less_than_one,
                    value_at_zero = self.value_at_zero,
                )
            )

            # Add to total freqs the amount we expect
            expected_N_frequencies += N

            # Add individual frequencies
            expected_frequencies.extend([freq + (i/100) for i in range(N)])
            
        # Return info
        return {
            "original_sample_rate": config_dict["original_sample_rate"],
            "target_sample_rate": config_dict["target_sample_rate"],
            "expected_N_frequencies": expected_N_frequencies,
            "expected_frequencies": expected_frequencies,
            "start_freq": start_freq,
            "end_freq": end_freq,
        }

    # Set up a configuration list of dicts, They can look like this:
    """
    [ {
        "original_sample_rate": 48000,
        "target_sample_rate": 5000,
        "start_freq": 20,
        "end_freq": 2500,
    }, {
        ...
    }]
    """
    # NOTE: The FFT will only get values of frequencies up to SAMPLE_RATE/2 and jumps of
    # the calculation sample rate divided by the window size (batch size)
    # So if you want more bass information, downsample to 5000 Hz or 1000 Hz and get frequencies
    # up to 2500 or 500, respectively.
    def configure(self, config, where_decay_less_than_one = 440, value_at_zero = 3):
        debug_prefix = "[AudioProcessing.configure]"

        logging.info(f"{debug_prefix} Whole notes frequencies we'll care: [{self.piano_keys_frequencies}]")

        # Assign
        self.config = config
        self.FFT_length = 0
        self.where_decay_less_than_one = where_decay_less_than_one
        self.value_at_zero = value_at_zero

        # The configurations on sample rate, frequencies to expect
        self.process_layer_configs = []

        # For every config dict on the config
        for layers in self.config:
            info = self._get_config_stuff(layers)
            self.FFT_length += info["expected_N_frequencies"] * 2
            self.process_layer_configs.append(info)

        # The size will be half, because left and right channel so we multiply by 2
        # self.FFT_length *= 2
        print("BINNED FFT LENGTH", self.FFT_length)

    # # Feature Extraction

    # Calculate the Root Mean Square
    def rms(self, values: np.ndarray) -> float:
        return np.sqrt(np.mean(values ** 2))

    # # New Methods

    # Yield information on the audio slice
    def get_info_on_audio_slice(self, audio_slice: np.ndarray, original_sample_rate, do_calculate_fft = True) -> dict:
        N = audio_slice.shape[1]

        # Calculate MONO
        mono = (audio_slice[0] + audio_slice[1]) / 2

        yield ["mmv_raw_audio_left", audio_slice[0]]
        yield ["mmv_raw_audio_right", audio_slice[1]]

        # # Average audio amplitude based on RMS

        # L, R, Mono respectively
        RMS = []

        # Iterate, calculate the median of the absolute values
        for channel_number in [0, 1]:
            RMS.append(np.sqrt(np.mean(audio_slice[channel_number][0:N] ** 2)))
            # RMS.append(np.median(np.abs(audio_slice[channel_number][0:N//120])))
        
        # Append mono average amplitude
        RMS.append(sum(RMS) / 2)

        # Yield average amplitudes info
        yield ["mmv_rms", tuple([round(value, 8) for value in RMS])]

        # # Standard deviations

        yield ["mmv_std", tuple([
            np.std(audio_slice[0]),
            np.std(audio_slice[1]),
            np.std(mono)
        ])]

        # # FFT shenanigans
        if do_calculate_fft:

            # The final fft we give to the shader
            processed = np.zeros(self.FFT_length, dtype = np.float32)

            # Counter to assign values on the processed array
            counter = 0

            # For each channel
            for channel_index, data in enumerate(audio_slice):

                # For every config dict on the config
                for info in self.process_layer_configs:
               
                    # Sample rate
                    original_sample_rate = info["original_sample_rate"]
                    target_sample_rate = info["target_sample_rate"]

                    # Individual frequencies
                    expected_frequencies = info["expected_frequencies"]

                    # The FFT of [[frequencies], [values]]                    
                    binned_fft = self.fourier.binned_fft(
                        data = self.resample(
                            data = data,
                            original_sample_rate = original_sample_rate,
                            target_sample_rate = target_sample_rate,
                        ),

                        original_sample_rate = original_sample_rate,
                        target_sample_rate = target_sample_rate,
                    )
                    if binned_fft is None: return

                    # Information on the frequencies, the index 0 is the DC bias, or frequency 0 Hz
                    # and at every index it jumps the distance between any index N and N+1
                    fft_freqs = binned_fft[0]
                    jumps = abs(fft_freqs[1])

                    # Reverse the second channel frequencies for continuity
                    if channel_index:
                        expected_frequencies = reversed(expected_frequencies)

                    # Get the nearest freq and add to processed         
                    for freq in expected_frequencies:

                        # TODO: make configurable
                        flatten_scalar = self.functions.value_on_line_of_two_points(
                            Xa = 20, Ya = 0.1,
                            Xb = 20000, Yb = 3,
                            get_x = freq
                        )

                        # # Get the nearest and FFT value

                        # Trick: since the jump of freqs are always the same, the nearest frequency index
                        # given a target freq will be the frequency itself divided by how many frequency we
                        # jump at the indexes
                        nearest = int(freq / jumps)

                        # The abs value of the FFT
                        value = abs(binned_fft[1][nearest]) * flatten_scalar

                        # Assign, iterate
                        processed[counter] = value
                        counter += 1

            # Yield FFT data
            yield ["mmv_fft", processed]

    # # Common Methods

    # Resample an audio slice (raw array) to some other frequency, this is useful when calculating
    # FFTs because a lower sample rate means we get more info on the bass freqs
    def resample(self,
            data: np.ndarray,
            original_sample_rate: int,
            target_sample_rate: int
    ) -> np.ndarray:

        # If the ratio is 1 then we don't do anything cause new/old = 1, just return the input data
        if target_sample_rate == original_sample_rate:
            return data

        # Use libsamplerate for resampling the audio otherwise
        return samplerate.resample(data, ratio = (target_sample_rate / original_sample_rate), converter_type = 'sinc_fastest')

    # Resample the data with nearest index approach
    # Doesn't really work, experimental, maybe I understand resampling wrong
    def resample_nearest(self,
            data: np.ndarray,
            original_sample_rate: int,
            target_sample_rate: int
    ) -> np.ndarray:

        # Nothing to do, target sample rate is the same as old one
        if (target_sample_rate == original_sample_rate):
            return data
            
        # The ratio we'll resample
        ratio = (original_sample_rate / target_sample_rate)

        # Length of the data
        N = data.shape[0]

        # Target new array length
        T = N * ratio

        # Array of original indexes
        indexes = np.arange(T)

        # (indexes / T) is the normalized to max at 1, we multiply
        # by the length of the original data so we expand the indexes
        # we just shaved by N * ratio, then use integer numbers and 
        # offset by 1
        indexes = ((indexes / T) * N).astype(np.int32) - 1

        # Return the original data with selected indexes
        return data[indexes] 

    # Get N semitones above / below A4 key, 440 Hz
    #
    # get_frequency_of_key(-12) = 220 Hz
    # get_frequency_of_key(  0) = 440 Hz
    # get_frequency_of_key( 12) = 880 Hz
    #
    def get_frequency_of_key(self, n, A4 = 440):
        return A4 * (2**(n/12))

    # https://stackoverflow.com/a/2566508
    # Find nearest value inside one array from a given target value
    # I could make my own but this one is more efficient because it uses numpy
    # Returns: index of the match and its value
    def find_nearest(self, array, value):
        index = (np.abs(array - value)).argmin()
        return index, array[index]
    

    # # Old methods [compatibility]


    # Slice a mono and stereo audio data TODO: make this a generator and also accept "real time input?"
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

    # Calculate the FFT of this data, get only wanted frequencies based on the musical notes
    def process(self,
            data: np.ndarray,
            original_sample_rate: int,
        ) -> None:
        
        # The returned dictionary
        processed = {}

        # Iterate on config
        for layer in self.config:
            value = self._get_config_stuff(layer)

            # Get info on config
            original_sample_rate = value.get("original_sample_rate")
            target_sample_rate = value.get("target_sample_rate")
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
                    target_sample_rate = target_sample_rate,
                ),

                # # Target (re?)sample rate so we normalize the FFT values

                target_sample_rate =  target_sample_rate,
                original_sample_rate = original_sample_rate,
            )

            # Get the nearest freq and add to processed            
            for freq in wanted_freqs:

                # Get the nearest and FFT value
                nearest = self.find_nearest(binned_fft[0], freq)
                value = binned_fft[1][nearest[0]] * 0.2
     
                # How much bars we'll render duped at this freq, see
                # this function on the Functions class for more detail
                N = math.ceil(
                    self.functions.how_much_bars_on_this_frequency(
                        x = freq,
                        where_decay_less_than_one = self.where_decay_less_than_one,
                        value_at_zero = self.value_at_zero,
                    )
                )

                # Add repeated bars or just one, this is a hacky workaround since we
                # add a small fraction on the target freq, it shouldn't really overlap
                for i in range(N):
                    processed[nearest[1] + (i/10)] = value
        
        # FIXME: inefficient

        # # Convert a dictionary of FFTs to a list of values:frequencies
        # We can use a array with shape (N, 2) but I'm lazy to change that

        linear_processed_fft = []
        frequencies = []

        # For each pair in the dictionary, append to each list
        for frequency, value in processed.items():
            frequencies.append(frequency)
            linear_processed_fft.append(value)
        
        return [linear_processed_fft, frequencies]