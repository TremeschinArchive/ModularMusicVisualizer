"""
===============================================================================

Purpose: Abstract, wrap, connect other files

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

from mmv.mmvanimation import MMVAnimation
from mmv.controller import Controller
from mmv.audio import AudioProcessing
from mmv.video import FFmpegWrapper
from mmv.utils import Miscellaneous
from mmv.audio import AudioFile
from mmv.fourier import Fourier
from mmv.context import Context
from mmv.canvas import Canvas
from mmv.assets import Assets
from mmv.core import Core
from PIL import Image
import numpy as np
import argparse
import math
import time
import sys
import os


class MMVMain():
    def setup_input_audio_file(self):
        
        debug_prefix = "[MMVMain.setup_input_audio_file]"

        print(debug_prefix, "Reading AudioFile")
        self.audio.read(self.context.input_file)
        self.context.duration = self.audio.info["duration"]

    def setup(self, args={}, cli=False):

        debug_prefix = "[MMVMain.__init__]"

        print(debug_prefix, "Creating Context()")
        self.context = Context(args)
        # self.context.reset_directories()

        print(debug_prefix, "Creating Controller()")
        self.controller = Controller(self.context)

        print(debug_prefix, "Creating Canvas()")
        self.canvas = Canvas(self.context)

        print(debug_prefix, "Creating Assets()")
        self.assets = Assets(self.context)

        print(debug_prefix, "Creating Fourier()")
        self.fourier = Fourier()

        print(debug_prefix, "Creating FFmpegWrapper()")
        self.ffmpeg = FFmpegWrapper(self.context, self.controller)

        print(debug_prefix, "Making Directories")
        self.context.utils.mkdir_dne(
            self.context.processing
        )

        print(debug_prefix, "Creating AudioFile()")
        self.audio = AudioFile(self.context)

        print(debug_prefix, "Creating AudioProcessing()")
        self.audio_processing = AudioProcessing(self.context)

        print(debug_prefix, "Creating MMVAnimation()")
        self.mmvanimation = MMVAnimation(self.context, self.controller, self.audio, self.canvas)
    
        if cli:
            self.setup_input_audio_file()

        print(debug_prefix, "Creating Core()")
        self.core = Core(
            self.context,
            self.controller,
            self.canvas,
            self.assets,
            self.fourier,
            self.ffmpeg,
            self.audio,
            self.mmvanimation,
            self.audio_processing,
        )

    def run(self):

        self.ffmpeg.pipe_one_time(self.context.output_video)

        try:
            import cProfile
            p = cProfile.Profile()
            p.enable()
            self.core.run()
            p.disable()
            p.dump_stats("res.prof")
        except KeyboardInterrupt:
            sys.exit(-1)

if __name__ == "__main__":

    # Greeter message :)
    Miscellaneous()
    
    # Create ArgumentParser
    args = argparse.ArgumentParser(description='Arguments for Modular Music Visualizer')

    # Add arguments
    args.add_argument('-i', '--input_file', required=True, help="(string) Input audio to generate final video, if not .wav uses ffmpeg to convert")
    args.add_argument("-p", "--preset", required=False, help="(string) Resolution and FPS presets [low, medium, high, ultra, max] (low, medium, high, ultra, max respectively)")
    args.add_argument("-m", "--multiprocessed", required=False, action="store_true", help="(solo) Use multiprocessing with svg rasterizer")
    args.add_argument("-w", "--workers", required=False, help="(int) Multiprocessing Process count, defaults to system number of threads")

    # Parse and organize the arguments
    args = args.parse_args()
    args = {
        "input_file": args.input_file,
        "preset": args.preset,
        "multiprocessed": args.multiprocessed,
        "workers": args.workers,
    }

    mmv = MMVMain(cli=True)
    mmv.setup(args)
    mmv.run()