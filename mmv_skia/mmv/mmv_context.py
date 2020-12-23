"""
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

from mmv.common.cmn_constants import NEXT_DEPTH, NO_DEPTH
import logging
import sys
import os


class MMVPath:
    def __init__(self, mmv_main, depth = NO_DEPTH):
        debug_prefix = "[MMVPath.__init__]"
        ndepth = depth + NEXT_DEPTH
        self.mmv_main = mmv_main

        # The root directory we'll be refering to, it's the folder where __init__.py is located
        # We need to get the mmv_main's interface class position as the "package mmv" is the interface itself
        self.ROOT = self.mmv_main.interface.ROOT

        # Path separator
        sep = os.path.sep

        # # Externals directory (ffmpeg binaries mainly on Windows)
        
        # Define it
        self.externals_dir = f"{self.ROOT}{sep}externals"
        logging.info(f"{depth}{debug_prefix} Externals folder path is: [{self.externals_dir}]")
            
        # Make the directory if it doesn't exist
        logging.info(f"{depth}{debug_prefix} Make directory if doesn't exist Externals Directory")
        self.mmv_main.utils.mkdir_dne(self.externals_dir, depth = ndepth)

        # Append to PATH the 
        logging.info(f"{depth}{debug_prefix} Appending Externals Directory to system PATH environment variable")
        sys.path.append(self.externals_dir)

        # # Data directory (configurations)

        self.data_dir = f"{self.ROOT}{sep}data"
        logging.info(f"{depth}{debug_prefix} Data folder path is: [{self.data_dir}]")

        # # Error assertion the directories

        self.error_assertion(depth = ndepth)

    # Make sure the directories and files we'll need exist (required ones)
    def error_assertion(self, depth = NO_DEPTH):
        debug_prefix = "[MMVPath.error_assertion]"
        ndepth = depth + NEXT_DEPTH

        # # Directories
        
        # Data directory
        self.mmv_main.utils.assert_dir(self.data_dir, depth = ndepth)
        

class MMVContext:
    def __init__(self, mmv_main, depth = NO_DEPTH) -> None:
        debug_prefix = "[MMVContext.__init__]"
        ndepth = depth + NEXT_DEPTH
        self.mmv_main = mmv_main

        # TODO: Load from config file
        self.HARD_DEBUG = True

        # Create classes
        logging.info(f"{depth}{debug_prefix} Creating MMVPath() class")
        self.paths = MMVPath(self.mmv_main, ndepth)

        # Files, info
        self.output_video = None
        self.input_file = None
        self.input_midi = None
        self.duration = None

        # External dependencies directory
        self.data_dir = self.paths.ROOT + "/data"

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