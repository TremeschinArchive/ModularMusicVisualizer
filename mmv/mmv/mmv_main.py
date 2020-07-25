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

from mmv.common.cmn_audio import AudioProcessing
from mmv.common.cmn_video import FFmpegWrapper
from mmv.mmv_animation import MMVAnimation
from mmv.common.cmn_audio import AudioFile
from mmv.common.cmn_fourier import Fourier
from mmv.mmv_controller import Controller
from mmv.mmv_context import Context
from mmv.mmv_image import MMVImage
from mmv.mmv_core import Core
from PIL import Image
import numpy as np
import argparse
import shutil
import math
import time
import sys
import os


class Miscellaneous():

    def __init__(self) -> None:
        self.version = "1.4.8-working-dev"
        self.greeter_message()

    def greeter_message(self) -> None:

        terminal_width = shutil.get_terminal_size()[0]

        bias = " "*(math.floor(terminal_width/2) - 14)

        message = f"""
{"-"*terminal_width}
{bias} __  __   __  __  __     __
{bias}|  \/  | |  \/  | \ \   / /
{bias}| |\/| | | |\/| |  \ \ / / 
{bias}| |  | | | |  | |   \ V /  
{bias}|_|  |_| |_|  |_|    \_/   
{bias}
{bias}  Modular Music Visualizer                        
{bias}{(21-len("Version")-len(self.version))*" "}Version {self.version}
{"-"*terminal_width}
"""
        print(message)


class MMVMain:

    def __init__(self, quiet: bool=False) -> None:
        if not quiet:
            Miscellaneous()
    
    # Creates classes and send to Core
    def setup(self, args: dict={}, cli: bool=False) -> None:

        debug_prefix = "[MMVMain.__init__]"

        print(debug_prefix, "Creating Context()")
        self.context = Context(args)

        print(debug_prefix, "Creating Controller()")
        self.controller = Controller(self.context)

        print(debug_prefix, "Creating Canvas()")
        self.canvas = MMVImage(self.context)
        self.canvas.create_canvas()

        print(debug_prefix, "Creating Fourier()")
        self.fourier = Fourier()

        print(debug_prefix, "Creating FFmpegWrapper()")
        self.ffmpeg = FFmpegWrapper(self.context, self.controller)

        print(debug_prefix, "Creating AudioFile()")
        self.audio = AudioFile(self.context)

        print(debug_prefix, "Creating AudioProcessing()")
        self.audio_processing = AudioProcessing(self.context)

        print(debug_prefix, "Creating MMVAnimation()")
        self.mmvanimation = MMVAnimation(self.context, self.controller, self.audio, self.canvas)
    
        print(debug_prefix, "Creating Core()")
        self.core = Core(
            self.context,
            self.controller,
            self.canvas,
            self.fourier,
            self.ffmpeg,
            self.audio,
            self.mmvanimation,
            self.audio_processing,
        )

    # Execute the program
    def run(self) -> None:
        
        # Read the audio and start FFmpeg pipe
        self.audio.read(self.context.input_file)
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
