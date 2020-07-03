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

from scipy.io import wavfile
import numpy as np
import subprocess
import soundfile
import os


class Audio():
    def __init__(self, context):
        self.context = context

    def set_audio_file(self, audio):

        debug_prefix = "[Audio.set_audio_file]"

        if not audio.endswith(".wav"):
            print(debug_prefix, "Audio does not end with .wav")
            output = self.context.processing + os.path.sep + self.context.utils.get_filename_no_extension(audio) + ".wav"
            print(debug_prefix, "Processing .wav audio file will be [%s]" % output)
            if not os.path.exists(output):
                print(debug_prefix, "Processing .wav audio file does not exist")
                command = ["ffmpeg", "-i", audio, "-b:a", "300k", output]
                print(debug_prefix, "Converting to .wav with command:", command)
                subprocess.run(command)
            else:
                print(debug_prefix, "Processing .wav audio file exists")

            self.context.input_file = output
            print(debug_prefix, "context.input_file is now [%s]" % self.context.input_file)

    def read(self, audio):

        debug_prefix = "[Audio.read]"

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

        self.data = np.zeros([self.info["channels"], len(data)])

        print(debug_prefix, "Parsing data")
        for index in range(len(data)):
            value = data[index]
            for position in range(self.info["channels"]):
                self.data[position][index] = value[position]
        
        print("asdasd")
        for item in self.data:
            print(item)

        print(debug_prefix, "Parsed data")
        print(debug_prefix, "Data is:", self.data)
        print(debug_prefix, "Len data:", len(self.data))
        print(debug_prefix, "Len data[0]:", len(self.data[0]))
        
    def get_info(self, path):

        info = soundfile.SoundFile(path)

        self.info = {
            "sample_rate": info.samplerate,
            "channels": info.channels,
            "subtype": info.subtype,
        }

        self.info["bit_depth"] = int(self.info["subtype"].split("_")[1])
