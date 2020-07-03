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
        
        self.processing = self.utils.ROOT + os.path.sep + "processing"
        self.data = self.utils.ROOT + os.path.sep + "data"

        self.input_file = None

        self.batch_size = 512
        self.nbatches = None

        self.width = 1280
        self.height = 720

