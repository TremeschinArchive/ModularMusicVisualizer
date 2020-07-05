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

from PIL import ImageFilter
from utils import Utils
from PIL import Image
import numpy as np
import imageio
import numpy
import time
import copy
import sys
import os


class Frame():
    def __init__(self):
        self.utils = Utils()

    # Create new numpy array as a "frame", attribute width, height and resolution
    def new(self, width, height, transparent=False):
        if transparent:
            channels = 4
        else:
            channels = 3
            
        self.frame = np.zeros([height, width, channels], dtype=np.uint8)
        self.width = width
        self.height = height
        self.resolution = (width, height)
        self.name = ''

    # Load image from a given path
    def load_from_path(self, path, convert_to_png=False):

        debug_prefix = "[Frame.load_from_path]"

        # print(debug_prefix, path)

        # Keep trying to read it
        while True:
            try:
                # self.frame = imageio.imread(path).astype(np.uint8)
                self.original_image = Image.open(path)
                if convert_to_png:
                    self.original_image = self.original_image.convert("RGBA")
                self.image = copy.deepcopy(self.original_image)
                self.frame = np.array(self.image)
                break
            except Exception:
                pass
            time.sleep(0.1)

        self.height = self.image.size[0]
        self.width = self.image.size[1]
        self.resolution = (self.width, self.height)
        self.name = path

    # Wait until a file exist and then load it as a image
    def load_from_path_wait(self, path, convert_to_png=False):
        self.utils.until_exist(path)
        self.load_from_path(path, convert_to_png=convert_to_png)

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
    
    def resize_by_ratio(self, ratio):

        debug_prefix = "[Frame.resize_by_ratio]"

        new_width = int(self.width * ratio)
        new_height = int(self.height * ratio)

        self.image = self.original_image.resize((new_width, new_height), Image.ANTIALIAS)
        self.frame = np.array(self.image)

        # print(debug_prefix, self.width, self.height, new_width, new_height, ratio)
        # print(self.frame.shape)

        # Return the offset to preserve the center
        return [
            (self.width - new_width)/2,
            (self.height - new_height)/2
        ]
    
    def resize_to_resolution(self, width, height, override=False):
        if override:
            self.original_image = self.original_image.resize((width, height), Image.ANTIALIAS)
            self.image = self.original_image
            self.frame = np.array(self.image)
            self.height = self.frame.shape[0]
            self.width = self.frame.shape[1]
        else:
            self.image = self.original_image.resize((width, height), Image.ANTIALIAS)
            self.frame = np.array(self.image)
    
    def gaussian_blur(self, radius):
        # print("Gaussian", radius)
        self.image = self.image.filter(ImageFilter.GaussianBlur(radius=radius))
        self.frame = np.array(self.image)

    # https://stackoverflow.com/questions/52702809/copy-array-into-part-of-another-array-in-numpy
    def copy_from(self, A, B, A_start, B_start, B_end):
        """
        A_start is the index with respect to A of the upper left corner of the overlap
        B_start is the index with respect to B of the upper left corner of the overlap
        B_end is the index of with respect to B of the lower right corner of the overlap
        """

        debug_prefix = "[Frame.copy_from]"

        A_start, B_start, B_end = map(np.asarray, [A_start, B_start, B_end])
        shape = B_end - B_start
        resolution = B.shape

        # print(debug_prefix, "starting from args = {%s, %s, %s, %s}" % (A_start, B_start, B_end, shape))
        
        # If B_start is before zero, A_start is that offset and B_start is zero
        for i in range(2):
            if B_start[i] < 0:
                # print("A start changing", A_start[i], - B_start[i])
                A_start[i] = - B_start[i]
                # B_end[i] -= B_start[i]
                B_start[i] = 0
                # shape = B_end - B_start
                # A = A[
                #     0:shape[0],
                #     0:shape[1]
                # ]

        # Ignore negative shapes, error (?)
        if any([shape[i] < 0 for i in range(2)]):
            # print(debug_prefix, "NEGATIVE SHAPE")
            return

        # [Out of Bounds] We offsetted A_start if B_start is before zero
        # so if the size of the shape is entirely out of bounds
        if A_start[0] >= shape[0] or A_start[1] >= shape[1]:
            # print("RETURN A")
            return

        # [Out of Bounds] B_start is bigger than the B's resolution on that axis
        if B_start[0] >= resolution[0] or B_start[1] >= resolution[1]:
            # print("RETURN B")
            return

        # # Bottom and right edge out of bounds

        # End is bigger than resolution
        # for i in range(2):
        #     if B_end[i] >= resolution[i]:
        #         print("A", B_end[i], resolution[i])
        #         B_end[i] = resolution[i] - 1
        #         print("AA", B_end[i])
                
        # Start + shape is bigger than resolution
        for i in range(2):
            if B_start[i] + shape[i] >= resolution[i]:
                # print("B", B_start[i], shape[i], resolution[i], B_end[i])
                B_end[i] = resolution[i] - 1

        # Shape is bigger than resolution, cut it
        if any([shape[i] >= resolution[i] for i in range(2)]):

            for i in range(2):
                B_end[i] = resolution[i]

            cut = [
                min(resolution[0], B_start[0] + shape[0] + 1),
                min(resolution[1], B_start[1] + shape[1] + 1)
            ]
            cut[0] += A_start[0]
            cut[1] += A_start[1]

            A = A[
                0:cut[0],
                0:cut[1]
            ]

            # print(">>>> CUT A", cut, A.shape)
        
        shape = B_end - B_start
        
        # print(debug_prefix, "Copying from, args = {%s, %s, %s, %s}" % (A_start, B_start, B_end, shape))

        try:
            B_slices = tuple(map(slice, B_start, B_end + 1))
            A_slices = tuple(map(slice, A_start, A_start + shape + 1))

            B[B_slices] = A[A_slices]

            # print(debug_prefix, "Copied from, args = {%s, %s, %s}" % (A_start, B_start, B_end))

        except ValueError as e:
            print(debug_prefix, "Fatal error copying block: ", e)
            sys.exit(-1)

    # TODO: THIS FUNCTION IS HELL SLOW
    def overlay_transparent(self, overlay, x, y):

        positioned = Frame()
        positioned.new(self.width, self.height, transparent=True)

        overlay_resolution = overlay.shape
        overlay_width = overlay_resolution[0]
        overlay_height = overlay_resolution[1]

        positioned.copy_from(
            overlay,
            positioned.frame,
            [0, 0],
            [x, y],
            [x + overlay_width - 1, y + overlay_height - 1]
        )

        self.image = Image.alpha_composite(self.image_array(), positioned.image_array())

        self.frame = np.array(self.image)
