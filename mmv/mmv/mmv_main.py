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

from mmv.pyskt.skia_no_window_backend import SkiaNoWindowBackend
from mmv.common.cmn_coordinates import PolarCoordinates
from mmv.common.cmn_interpolation import Interpolation
from mmv.common.cmn_audio import AudioProcessing
from mmv.common.cmn_functions import Functions
from mmv.common.cmn_video import FFmpegWrapper
from mmv.mmv_animation import MMVAnimation
from mmv.common.cmn_audio import AudioFile
from mmv.common.cmn_fourier import Fourier
from mmv.common.cmn_utils import Utils
from mmv.mmv_context import MMVContext
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


class Miscellaneous:
    def __init__(self) -> None:
        self.version = "2.3.4-dev"
        self.greeter_message()

    def greeter_message(self) -> None:

        terminal_width = shutil.get_terminal_size()[0]

        bias = " "*(math.floor(terminal_width/2) - 14)

        message = \
f"""{"-"*terminal_width}
{bias} __  __   __  __  __     __
{bias}|  \\/  | |  \\/  | \\ \\   / /
{bias}| |\\/| | | |\\/| |  \\ \\ / / 
{bias}| |  | | | |  | |   \\ V /  
{bias}|_|  |_| |_|  |_|    \\_/   
{bias}
{bias}  Modular Music Visualizer                        
{bias}{(21-len("Version")-len(self.version))*" "}Version {self.version}
{"-"*terminal_width}
"""
        print(message)


class MMVMain:
    def __init__(self) -> None:
        Miscellaneous()
    
    # Creates classes and send to Core
    def setup(self) -> None:
        
        debug_prefix = "[MMVMain.setup]"

        self.utils = Utils()

        print(debug_prefix, "Creating MMVContext()")
        self.context = MMVContext(self)

        print(debug_prefix, "Creating SkiaNoWindowBackend()")
        self.skia = SkiaNoWindowBackend()

        print(debug_prefix, "Creating Functions()")
        self.functions = Functions()

        print(debug_prefix, "Creating Interpolation()")
        self.interpolation = Interpolation()

        print(debug_prefix, "Creating PolarCoordinates()")
        self.polar_coordinates = PolarCoordinates()

        print(debug_prefix, "Creating Canvas()")
        self.canvas = MMVImage(self)

        print(debug_prefix, "Creating Fourier()")
        self.fourier = Fourier()

        print(debug_prefix, "Creating FFmpegWrapper()")
        self.ffmpeg = FFmpegWrapper(self)

        print(debug_prefix, "Creating AudioFile()")
        self.audio = AudioFile()

        print(debug_prefix, "Creating AudioProcessing()")
        self.audio_processing = AudioProcessing()

        print(debug_prefix, "Creating MMVAnimation()")
        self.mmv_animation = MMVAnimation(self)
    
        print(debug_prefix, "Creating Core()")
        self.core = Core(self)

    # Execute the program
    def run(self) -> None:
        debug_prefix = "[MMVMain.run]"
        
        # Read the audio and start FFmpeg pipe
        print(debug_prefix, "Read audio file")
        self.audio.read(self.context.input_file)
        
        # Start video pipe
        print(debug_prefix, "Starting FFmpeg Pipe")
        self.ffmpeg.pipe_one_time(self.context.output_video)

        try:
            # import cProfile
            # p = cProfile.Profile()
            # p.enable()
            print(debug_prefix, "Executing MMVCore.run()")
            self.core.run()
            
            print(debug_prefix, "Finished, terminating GLFW")
            self.skia.terminate_glfw()
            # p.disable()
            # p.dump_stats("res.prof")
        except KeyboardInterrupt:
            self.skia.terminate_glfw()
            sys.exit(-1)
        
        # # Print thanks message :)

        message = \
"""
         :: Thanks for using the Modular Music Visualizer project !! ::

  Here's a few official links regarding MMV:

  - Telegram group:                      [ https://t.me/modular_music_visualizer ]
  - GitHub Repository:  [ https://github.com/Tremeschin/modular-music-visualizer ]
  - GitLab Repository:  [ https://gitlab.com/Tremeschin/modular-music-visualizer ]
"""
        print(message)
