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

from mmv.common.utils import Utils
import os


class Context:
    def __init__(self, args: dict) -> None:

        self.args = args

        # Utils class and ROOT dir
        self.utils = Utils()
        self.ROOT = self.utils.ROOT

        # The operating system we're workingon
        self.os = self.utils.get_os()
        
        # Directories
        self.data = self.ROOT + os.path.sep + "data"
        self.assets = self.ROOT + os.path.sep + "assets"

        # Files, info
        self.output_video = None
        self.input_file = None
        self.duration = None

        # Video specs
        self.width = 1280
        self.height = 720
        self.fps = 60

        # # Batchs, responsiveness
        self.batch_size = 2048 #(48000 // self.fps) # 512

        # Offset the audio slice by this much of steps
        self.offset_audio_before_in_many_steps = (60/self.fps) // 8

        # Performance
        self.svg_rasterizer = "cairo"
        self.multiprocessed = False
        self.multiprocessing_workers = 4

        # User
        self.watch_processing_video_realtime = False
