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


class Context():
    def __init__(self, args):

        self.args = args

        self.utils = Utils()
        self.ROOT = self.utils.ROOT

        self.os = self.utils.get_os()
        
        # Directories
        self.processing = self.ROOT + os.path.sep + "processing"
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

        self.process_args()

    def process_args(self):
        
        keys = list(self.args.keys())
        
        # User chose a preset
        if not (preset := self.args["preset"] if "preset" in keys else None) == None:
            self.preset(preset)

        if not (multiprocessed := self.args["multiprocessed"] if "multiprocessed" in keys else None) == None:
            self.multiprocessed = multiprocessed
        
        if not (workers := int(self.args["workers"]) if "workers" in keys else None) == None:
            self.multiprocessing_workers = workers
        
        if not (input_file := self.args["input_file"] if "input_file" in keys else None) == None:
            self.input_file = input_file

    # Delete and create (reset) the runtime directories
    def reset_directories(self):
        for d in []:
            self.utils.rmdir(d)
            self.utils.mkdir_dne(d)
