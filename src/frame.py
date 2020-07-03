"""
===============================================================================

Purpose: Wrapper for Numpy arrays and PIL Image, we call images Frames
Can load, copy, duplicate, save and substitute vectors of pixels

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
from PIL import Image
import numpy as np
import imageio
import numpy
import time
import os


class Frame():
    def __init__(self):
        self.utils = Utils()

    def new(self, width, height):
        self.frame = np.zeros([height, width, 3], dtype=np.uint8)
        self.width = width
        self.height = height
        self.resolution = (width, height)
        self.name = ''

    def load_from_path(self, filename):

        while True:
            try:
                self.frame = imageio.imread(filename).astype(np.uint8)
                break
            except Exception:
                pass
            time.sleep(0.1)

        self.height = self.frame.shape[0]
        self.width = self.frame.shape[1]
        self.resolution = (self.width, self.height)
        self.name = filename

    def load_from_path_wait(self, filename):
        self.utils.until_exist(filename)

    # Get PIL image array from this object frame
    def image_array(self):
        return Image.fromarray(self.frame.astype(np.uint8))

    # Save an image with specific instructions depending on it's extension type.
    def save(self, directory):

        debug_prefix = "[Frame.save]"

        print(debug_prefix, "Saving to file: [%s]" % directory)

        if '.jpg' in directory:
            jpegsave = self.image_array()
            jpegsave.save(directory, format='JPEG', subsampling=0, quality=100)

        elif ".png" in directory:
            save_image = self.image_array()
            save_image.save(directory, format='PNG')
            