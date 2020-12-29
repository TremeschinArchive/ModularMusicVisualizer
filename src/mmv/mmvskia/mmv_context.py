"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Global variables / settings across files

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
import logging
import sys
import os


# Also see __init__.py with MMVSkiaInterface
# that class also changes some configurations here, this is motly
# shared stuff across files and it's a bit hard to keep track of them all
class MMVContext:
    def __init__(self, mmv_main, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVContext.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_main = mmv_main

        # Files, info
        self.output_video = None
        self.input_audio_file = None
        self.input_midi = None
        self.duration = None

        # Video specs
        self.width = 1280
        self.height = 720
        self.fps = 60
        self.pixel_format = "auto"

        # # Overhaul "resolution" of the FFT, 512 low poly, 2048 balanced, 4096 + accurate
        # # Performance decreases with higher values
        self.batch_size = 2048  # (48000 // self.fps) # 512

        # Offset the audio slice by this much of steps
        self.offset_audio_before_in_many_steps = (60/self.fps) // 8

        # Default attribution to resolution ratio
        self.resolution_ratio_multiplier = (1 / 720) * self.height

        # Current processing time
        self.current_time = 0

        # User
        self.watch_processing_video_realtime = False
        self.audio_amplitude_multiplier = 1

        # Use "gpu" or "cpu" render backend?
        self.skia_render_backend = "gpu"

    def update_biases(self):

        # This is a scalar value that says what percentage of a 720p resolution
        # this video will be rendered with, for fixing incorrect sizing and
        # "adapting" the coordinates according to the resolution.
        # 
        # For a 720p ->  (1/720) * 720 = 1
        # For a 1080p ->  (1/720) * 1080 = 1.5
        #
        # That means a 1080p values need to be multiplied by 1.5 to match the values
        # on a 720p video as that's the default reference
        #
        self.resolution_ratio_multiplier = (1/720) * self.height
        self.fps_ratio_multiplier = 60 / self.fps

        # # Utils measurements

        # Size of the diagonal
        self.resolution_diagonal = round( (self.height**2 + self.width**2)**0.5, 2)

        print("[MMVContext.update_biases]", "Updated biases, here's a quick summary:", {
            "resolution_ratio_multiplier": self.resolution_ratio_multiplier,
            "fps_ratio_multiplier": self.fps_ratio_multiplier,
            "resolution_diagonal": self.resolution_diagonal,
        })