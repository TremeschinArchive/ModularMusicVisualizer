"""
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

from mmv.fourier import Fourier
from scipy.io import wavfile
import numpy as np
import subprocess
import samplerate
import soundfile
import os


class AudioFile():
    def __init__(self, context):
        self.context = context

    # Converts a file to .wav if it's not and move to the processing dir, sets the context.input_file var
    def set_audio_file(self, audio):

        debug_prefix = "[AudioFile.set_audio_file]"

        # AudioFile isn't an .wav
        if not audio.endswith(".wav"):
            print(debug_prefix, "AudioFile does not end with .wav")

            # Where the working .wav file will be saved
            output = self.context.processing + os.path.sep + self.context.utils.get_filename_no_extension(audio) + ".wav"
            print(debug_prefix, "Processing .wav audio file will be [%s]" % output)

            # If we haven't already converted to .wav the file into the directory
            if not os.path.exists(output):

                # Input original audio, output the .wav
                print(debug_prefix, "Processing .wav audio file does not exist")
                command = ["ffmpeg", "-i", audio, "-b:a", "300k", output]
            
                # Run the command
                print(debug_prefix, "Converting to .wav with command:", command)
                subprocess.run(command)

            else:
                # File already exists
                print(debug_prefix, "Processing .wav audio file exists")

            # Set the context.input_file to the output (.wav)
            self.context.input_file = output
            print(debug_prefix, "context.input_file is now [%s]" % self.context.input_file)

    # Read a .wav file from disk and gets the values on a list
    def read(self, audio):

        debug_prefix = "[AudioFile.read]"

        print(debug_prefix, "Setting audio file")
        self.set_audio_file(audio)

        print(debug_prefix, "Getting audio file info")
        self.get_info(self.context.input_file)

        print(debug_prefix, "Reading audio file data")
        self.fs, data = wavfile.read(self.context.input_file)

        print(debug_prefix, "Unparsed data info:")

        print(debug_prefix, "Data is:", data)
        print(debug_prefix, "Len data:", len(data))
        print(debug_prefix, "Len data[0]:", len(data[0]))

        self.stereo_data = data.T

        print(debug_prefix, "Transposed data")
        print(debug_prefix, "Data is", self.stereo_data)
        print(debug_prefix, "Shape data", self.stereo_data.shape)
        print(debug_prefix, "Len data:", self.stereo_data.shape[0])

        self.info["duration"] = self.stereo_data.shape[1] / self.info["sample_rate"]

        self.mono_data = (self.stereo_data[0] + self.stereo_data[1]) / 2

        print("Duration", self.info["duration"])

    # Get info from audio file - sample rate, channels, bit depth
    def get_info(self, path):

        info = soundfile.SoundFile(path)

        self.info = {
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "subtype": info.subtype,
        }

        self.info["bit_depth"] = int(self.info["subtype"].split("_")[1])


class AudioProcessing():
    def __init__(self, context):
        self.context = context
        self.fourier = Fourier()

    # Slice a mono and stereo audio data
    def slice_audio(self, stereo_data, mono_data, sample_rate, step):

        # The current time in seconds we're going to slice the audio based on its samplerate
        # If we offset to the opposite way, the starting point can be negative hence the max function.
        time_in_seconds = max( (1/self.context.fps) * step, 0 )

        # The current time in sample count to slice the audio
        this_time_in_samples = int(time_in_seconds * sample_rate)

        # The slice starts at the this_time_in_samples and end the cut here
        until = int(this_time_in_samples + self.context.batch_size)

        # Cut the left and right points range
        left_slice = stereo_data[0][this_time_in_samples:until]
        right_slice = stereo_data[1][this_time_in_samples:until]

        # Cut the mono points range
        mono_slice = mono_data[this_time_in_samples:until]

        # Empty audio slice array if we're at the end of the audio
        self.audio_slice = np.zeros([2, self.context.batch_size])

        # Get the audio slices of the left and right channel
        self.audio_slice[0][ 0:left_slice.shape[0] ] = left_slice
        self.audio_slice[1][ 0:right_slice.shape[0] ] = right_slice

        # # Calculate average amplitude
        
        # Normalize the mono data
        normalize_scalar = np.linalg.norm(mono_slice)
        if normalize_scalar > 0:
            normalized_mono_slice = mono_slice / normalize_scalar
        else:
            normalized_mono_slice = mono_slice
            
        self.average_value = np.mean(abs(normalized_mono_slice))


    def resample(self, data, original_sample_rate, new_sample_rate):
        ratio = new_sample_rate / original_sample_rate
        if ratio == 1:
            return data
        else:
            return samplerate.resample(data, ratio, 'sinc_best')

    def frequencies_in_between(self, data, start, end):
        return {k: v for k, v in d.iteritems() if k > start and k < end}
    
    def equal_slices(self, array, n):
        size = len(array)
        return [ array[i: min(i+n, size) ] for i in range(0, size, n) ]
    
    def equal_bars_average(self, data, nbars, mode):
        sorted_data = sorted(list(data.keys()))
        slices_index = self.equal_slices(sorted_data, nbars)

        return_values = [0 for _ in range(nbars)]
        
        if mode == "average":
            for bar_index, list_indexes in enumerate(slices_index):
                total_sum = 0
                for index in list_indexes:
                    total_sum += data[index]
                average = total_sum / len(list_indexes)
                return_values[bar_index] = average

        elif mode == "max":
            for bar_index, list_indexes in enumerate(slices_index):
                values = []
                for index in list_indexes:
                    values.append(data[index])
                return_values[bar_index] = max(values)
            
        return return_values

    def process(self, data, original_sample_rate):
        self.config = {
            "0": {
                "sample_rate": 1600,
                "get_frequencies": "range",
                "start_freq": 20,
                "end_freq": 800,
                "nbars": "original",
            },
            "1": {
                "sample_rate": 40000,
                "get_frequencies": "range",
                "start_freq": 800,
                "end_freq": 20000,
                "nbars": "300,average",
            },
        }

        # The returned dictionary
        processed = {}

        # Iterate on config
        for key, value in self.config.items():

            # Get info on config
            get_frequencies = value.get("get_frequencies")
            sample_rate = value.get("sample_rate")
            start_freq = value.get("start_freq")
            end_freq = value.get("end_freq")
            nbars = value.get("nbars")

            # Resample audio to target sample rate
            resampled = self.resample(data, original_sample_rate, sample_rate)

            # Get freqs vs fft value dictionary
            binned_fft = self.fourier.binned_fft(resampled, sample_rate)

            # Do we want every frequency of the binned_fft or a set of it
            if get_frequencies == "range":
                wanted_binned_fft = self.frequencies_in_between(binned_fft, start_freq, end_freq)
            elif get_frequencies == "all":
                wanted_binned_fft = binned_fft
            
            # Send the raw frequency vs fft dict 
            if nbars == "original":
                return wanted_binned_fft

            # Split "300,average" --> 300, "average" --> nbars and mode
            nbars, mode = nbars.split(",")

            # Split into average bars
            return self.equal_bars_average(wanted_binned_fft, int(nbars), mode)
