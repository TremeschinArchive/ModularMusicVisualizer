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

from glitch_this import ImageGlitcher
from mmv.common.cmn_types import *
from PIL import Image
import numpy as np
import numpy
import skia
import time
import copy
import sys
import cv2
import os

cv2.setNumThreads(12)

"""
This is (yet another) wrapper for images, but more focused on modularity
There are three variables you are interested in, those are image, original_image and array.
original_image is kept as a backup where you can just go back and revert all the processing you do
image is the current latest processed image, array is that image's raw data, both should be
linked again every time we process the image variable.

"""
class Frame:

    def __init__(self) -> None:
        # Multiprocessing pending things to do, ordered
        self.pending = {}
        self.size = 1
        self.rotate_angle = 0
    
    # # Internal functions
    
    # if override: self.original_image <-- self.image
    def _override(self, override: bool) -> None:
        if override:
            # self.original_image = skia.Image.fromarray(self.image.toarray())
            self.original_image = self.image
    
    # self.image --> self.array
    def _update_array_from_image(self) -> None:
        self.array = np.array(self.image)
    
    # Update resolution from the array shape
    def _update_resolution(self) -> None:
        self.height = self.image.height()
        self.width = self.image.width()

    # self.image = self.original_image
    def _reset_to_original_image(self) -> None:
        # self.image = skia.Image.fromarray(self.original_image.toarray())
        self.image = self.original_image
    
    # Get the image we're process the effects on
    def _get_processing_image(self, from_current_frame: bool=False):
        if from_current_frame:
            return self.image
        else:
            return self.original_image

    # # User functions

    # Create new numpy array as a "frame", attribute width, height and resolution
    def new(self, width: Number, height: Number) -> None:
        self.load_from_array(
            np.zeros([height, width, 4], dtype=np.uint8)
        )

    # Load this image by array
    def load_from_array(self, array: np.ndarray, convert_to_png: bool=False) -> None:
        # Set the image
        self.original_image = skia.Image.fromarray(array)
        self.image = self.original_image

        # Update width, height info
        self.height = self.image.height()
        self.width = self.image.width()

    # Load image from a given path
    def load_from_path(self, path: str, convert_to_png: bool=False) -> None:

        debug_prefix = "[Frame.load_from_path]"

        tries = 0

        print("\n>>", debug_prefix, "Loading image from path %s " % path)

        # Keep trying to read it
        while True:
            tries += 1
            if tries > 10:
                print(debug_prefix, "Can't load [%s], looped [%s] times" % (path, tries))
            try:
                # Our untouched original image
                # self.original_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                self.original_image = skia.Image.open(path)
                break # the while loop
            except Exception as e:
                print(e)
            time.sleep(0.1)
        
        # Warn the use rwe're not stuck anymore        
        if tries > 10:
            print(debug_prefix, "Could read image from path [%s]" % path)
        
        # Copy the original image
        self.image = self.original_image

        self._update_resolution()

    # Save an image with specific instructions depending on it's extension type.
    def save(self, path: str) -> None:
        self.image.save(path, skia.kJPEG)
    
    # Resize this frame multiplied by a scalar
    #
    # @ratio: scalar to multiply
    # @override: set the original image to the new resized one
    # @from_current_frame: resize not the original image but the current self.array, overrided by override
    #
    # Returns: offset array because of the resized new width and height according to the top left corner
    def resize_by_ratio(self,
            ratio: Number,
            override: bool=False,
        ) -> list:  # Returns the offset because the resize

        ratio = 1

        print(id(self.image), id(self.original_image), self.width, self.height, ratio)

        # Calculate the new width and height
        new_width = int(self.width * ratio)
        new_height = int(self.height * ratio)

        # Already on resolution
        if (new_width == self.width) and (new_height == self.height):
            return [0, 0]

        diff = np.array([self.width - new_width, self.height, new_height])

        self.image = self.image.resize(new_width, new_height)

        self._override(override)
        self._update_resolution()

        # Return the offset to preserve the center
        return diff / 2

    # Resize this frame to a fixed resolution
    # @override: set the original image to the new resized one
    def resize_to_resolution(self,
            width: Number,
            height: Number,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        processing = self._get_processing_image(from_current_frame)
        self.image = processing.resize(width, height)

        self._override(override)
        self._update_resolution()
    
    # Rotate this frame by a certain angle
    # [ WARNING ] Better only to rotate square images
    # @override: set the original image to the new rotated
    def rotate(self,
            angle: Number,
        ) -> None:

        self.rotate_angle = angle

    # Multiply this image's frame alpha channel by that scalar
    # @ratio: 0 - 1 values
    def transparency(self,
            ratio: Number,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        return

        processing = self._get_processing_image(from_current_frame)

        # Split the original image's channels
        r, g, b, alpha = cv2.split(processing)

        # Multiply the alpha by that ratio
        alpha = np.array(alpha) * ratio

        # Stack the arrays into a new numpy array "as image"
        self.image = (np.dstack((r, g, b, alpha))).astype(np.uint8)

        self._override(override)
        self._update_array_from_image()

    # Apply vignetting on this image object
    # @x: X coordinate center of the effect
    # @y: Y coordinate center of the effect
    # @deviation_$: sigma of the gaussian kernel
    def vignetting(self,
            x: Number,
            y: Number,
            deviation_x: Number,
            deviation_y: Number,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        return

        processing = self._get_processing_image(from_current_frame)
        
        # Split the image into the channels
        red, green, blue, alpha = cv2.split(processing)

        # Get the rows and columns of the image
        img = np.array(self.original_image)
        rows, cols = img.shape[:2]

        # Calculate our mask
        a = cv2.getGaussianKernel(2*cols, deviation_x)[cols - x: 2 * cols - x]
        b = cv2.getGaussianKernel(2*rows, deviation_y)[rows - y: 2 * rows - y]
        c = b * a.T
        d = c/c.max()

        # Multiply the channels by the mask
        red = red * d
        green = green * d
        blue = blue * d

        # Stack the arrays into a new numpy array "as image"
        self.image = (np.dstack((red, green, blue, alpha))).astype(np.uint8)

        self._override(override)
        self._update_array_from_image()

    