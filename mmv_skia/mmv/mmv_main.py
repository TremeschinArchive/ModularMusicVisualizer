"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
from mmv.pyskt.pyskt_backend import SkiaNoWindowBackend
from mmv.common.cmn_coordinates import PolarCoordinates
from mmv.common.cmn_interpolation import Interpolation
from mmv.common.cmn_audio import AudioProcessing
from mmv.common.cmn_functions import Functions
from mmv.common.cmn_video import FFmpegWrapper
from mmv.common.cmn_download import Download
from mmv.mmv_animation import MMVAnimation
from mmv.common.cmn_audio import AudioFile
from mmv.common.cmn_fourier import Fourier
from mmv.common.cmn_utils import Utils
from mmv.mmv_context import MMVContext
from mmv.mmv_image import MMVImage
from mmv.mmv_core import MMVCore
from PIL import Image
import numpy as np
import argparse
import logging
import math
import time
import sys
import os


class MMVMain:
    def __init__(self, interface):
        self.interface = interface
        self.prelude = self.interface.prelude
        
    # Creates classes and send to Core
    def setup(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVMain.setup]"
        ndepth = depth + LOG_NEXT_DEPTH

        self.utils = Utils()

        logging.info(f"{depth}{debug_prefix} Creating MMVContext() class")
        self.context = MMVContext(mmv_main = self, depth = ndepth)

        logging.info(f"{depth}{debug_prefix} Creating SkiaNoWindowBackend() class")
        self.skia = SkiaNoWindowBackend()

        logging.info(f"{depth}{debug_prefix} Creating Functions() class")
        self.functions = Functions()

        logging.info(f"{depth}{debug_prefix} Creating Interpolation() class")
        self.interpolation = Interpolation()

        logging.info(f"{depth}{debug_prefix} Creating PolarCoordinates() class")
        self.polar_coordinates = PolarCoordinates()

        logging.info(f"{depth}{debug_prefix} Creating Canvas() class")
        self.canvas = MMVImage(mmv_main = self, depth = ndepth)

        logging.info(f"{depth}{debug_prefix} Creating Fourier() class")
        self.fourier = Fourier()

        logging.info(f"{depth}{debug_prefix} Creating FFmpegWrapper() class")
        self.ffmpeg = FFmpegWrapper(self)

        logging.info(f"{depth}{debug_prefix} Creating AudioFile() class")
        self.audio = AudioFile()

        logging.info(f"{depth}{debug_prefix} Creating AudioProcessing() class")
        self.audio_processing = AudioProcessing()

        logging.info(f"{depth}{debug_prefix} Creating MMVAnimation() class")
        self.mmv_animation = MMVAnimation(mmv_main = self, depth = ndepth)
    
        logging.info(f"{depth}{debug_prefix} Creating MMVCore() class")
        self.core = MMVCore(mmv_main = self, depth = ndepth)

        logging.info(f"{depth}{debug_prefix} Creating Download() class")
        self.download = Download()

    # Execute the program
    def run(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVMain.run]"
        ndepth = depth + LOG_NEXT_DEPTH
        
        # Read the audio and start FFmpeg pipe
        logging.info(f"{depth}{debug_prefix} Read audio file")
        self.audio.read(self.context.input_file)
        
        # Start video pipe
        logging.info(f"{depth}{debug_prefix} Starting FFmpeg Pipe")
        self.ffmpeg.pipe_one_time(self.context.output_video)

        try:
            # import cProfile
            # p = cProfile.Profile()
            # p.enable()
            logging.info(f"{depth}{debug_prefix} Executing MMVCore.run()")
            self.core.run(depth = ndepth)
            
            logging.info(f"{depth}{debug_prefix} Finished, terminating GLFW")
            self.skia.terminate_glfw()
            # p.disable()
            # p.dump_stats("res.prof")
        except KeyboardInterrupt:
            self.skia.terminate_glfw()
            self.ffmpeg.close_pipe()
            sys.exit(-1)
        
        # Say thanks message
        self.thanks_message()

        # Wait for FFmpeg pipe to stop
        while not self.ffmpeg.stop_piping:
            time.sleep(0.05)

        logging.info(f"{depth}{debug_prefix} Quitting Python")
        sys.exit(0)
        

    def thanks_message(self):
        # # Print thanks message :)

        message = \
f"""
 [+-------------------------------------------------------------------------------------------+]
  |                                                                                           |
  |              :: Thanks for using the Modular Music Visualizer project !! ::               |
  |              ==============================================================               |
  |                                                                                           |
  |  Here's a few official links for MMV:                                                     |
  |                                                                                           |
  |    - Telegram group:          [          https://t.me/modular_music_visualizer         ]  |
  |    - GitHub Repository:       [ https://github.com/Tremeschin/modular-music-visualizer ]  |
  |    - GitLab Repository:       [ https://gitlab.com/Tremeschin/modular-music-visualizer ]  |
  |                                                                                           |
  |  > Always check for the copyright info on the material you are using (audios, images)     |
  |  before distributing the content generated with MMV, I take absolutely no responsibility  |
  |  for any UGC (user generated content) violations. See LICENSE file as well.               |
  |                                                                                           |
  |  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  |
  |                                                                                           |
  |             Don't forget sharing your releases made with MMV on the discussion groups :)  |
  |                 Feel free asking for help or giving new ideas for the project as well !!  |
  |                                                                                           |
 [+-------------------------------------------------------------------------------------------+]
"""
        print(message)