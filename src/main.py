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

from mmvanimation import MMVAnimation
from controller import Controller
from video import FFmpegWrapper
from utils import Miscellaneous
from fourier import Fourier
from context import Context
from canvas import Canvas
from assets import Assets
from audio import Audio
from frame import Frame
from core import Core
from PIL import Image
import numpy as np
import argparse
import math
import os


class MMV():
    def __init__(self, args):

        debug_prefix = "[MMV.__init__]"

        print(debug_prefix, "Creating Context()")
        self.context = Context()
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
        self.ffmpeg = FFmpegWrapper(self.context)

        self.context.input_file = args["input_file"]

        print(debug_prefix, "Making Directories")
        self.context.utils.mkdir_dne(
            self.context.processing
        )

        print(debug_prefix, "Creating Audio()")
        self.audio = Audio(self.context)

        print(debug_prefix, "Reading Audio")
        self.audio.read(self.context.input_file)
        self.context.duration = self.audio.info["duration"]

        print(debug_prefix, "Creating MMVAnimation()")
        self.mmvanimation = MMVAnimation(self.context, self.controller, self.canvas)

        print(debug_prefix, "Creating Core()")
        self.core = Core(
            self.context,
            self.controller,
            self.canvas,
            self.assets,
            self.fourier,
            self.ffmpeg,
            self.audio,
            self.mmvanimation
        )

        # # #

        self.ffmpeg.pipe_one_time(self.context.ROOT + os.path.sep + "demorun.mkv")
        self.core.start()


if __name__ == "__main__":

    # Greeter message :)
    Miscellaneous()
    
    # Create ArgumentParser
    args = argparse.ArgumentParser(description='Argu    ments for Modular Music Visualizer')

    # Add arguments
    args.add_argument('-i', '--input_file', required=True, help="(string) Input audio to generate final video, if not .wav uses ffmpeg to convert")
    args.add_argument("-p", "--profile", required=False, help="(string) Generate the video with that profile script under profiles dir")

    # Parse and organize the arguments
    args = args.parse_args()
    args = {
        "input_file": args.input_file,
        "profile": args.profile,
    }

    MMV(args)
