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

from utils import Utils
import os


class Context():
    def __init__(self):
        self.utils = Utils()
        self.ROOT = self.utils.ROOT
        
        # Directories
        self.processing = self.ROOT + os.path.sep + "processing"
        self.data = self.ROOT + os.path.sep + "data"
        self.assets = self.ROOT + os.path.sep + "assets"

        # Files
        self.input_file = None

        # Video specs
        self.width = 1920
        self.height = 1080
        self.fps = 60

        # Batchs, responsiveness
        self.batch_size = 48000//self.fps # 512
        self.duration = None

    # Delete and create (reset) the runtime directories
    def reset_directories(self):
        for d in []:
            self.utils.rmdir(d)
            self.utils.mkdir_dne(d)
