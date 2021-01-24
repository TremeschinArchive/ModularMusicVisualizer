"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

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

import mmv.common.cmn_any_logger
from PIL import Image
import numpy as np
import skia
import time
import copy
import sys
import cv2
import os

cv2.setNumThreads(12)

"""
original_image -> if we wanna "undo" all processing
image -> current processed image
"""
class Frame:
    def __init__(self) -> None:
        self.size = 1
    
    # # Internal functions
    
    # if override: self.original_image <-- self.image
    def _override(self, override: bool) -> None:
        if override:
            # self.original_image = skia.Image.fromarray(self.image.toarray())
            self.original_image = self.image
    
    # Update resolution from the array shape
    def _update_resolution(self) -> None:
        self.height = self.image.height()
        self.width = self.image.width()

    # Get the image we're process the effects on
    def _get_processing_image(self, from_current_frame: bool=False):
        if from_current_frame:
            return self.image
        else:
            return self.original_image

    # self.image = self.original_image
    def reset_to_original_image(self) -> None:
        # self.image = skia.Image.fromarray(self.original_image.toarray())
        if hasattr(self, "original_image"):
            self.image = self.original_image
            self._update_resolution()

    # # User functions

    # Create new numpy array as a "frame", attribute width, height and resolution
    def new(self, width: float, height: float) -> None:
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

        # Keep trying to read it
        while True:
            tries += 1
            if tries > 10:
                print(debug_prefix, "Can't load [%s], looped [%s] times" % (path, tries))
            try:
                # Our untouched original image
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
    #
    # Returns: offset array because of the resized new width and height according to the top left corner
    def resize_by_ratio(self,
            ratio: float,
            override: bool=False,
            from_current_frame: bool=True
        ) -> list:  # Returns the offset because the resize

        processing = self._get_processing_image(from_current_frame)

        # Calculate the new width and height
        new_width = int(self.width * ratio)
        new_height = int(self.height * ratio)

        # Already on resolution
        if (new_width == self.width) and (new_height == self.height):
            return [0, 0]

        diff = np.array([self.width - new_width, self.height - new_height])

        self.image = processing.resize(new_width, new_height)

        self._override(override)
        self._update_resolution()

        # Return the offset to preserve the center
        return diff / 2

    """
        Resize this frame to a fixed resolution
    kwargs: {
        "width": float, the width
        "height": float, the height
        "override": bool, False, replace the loaded image with this new resized one?
        "from_current_frame": bool, True, if False start from last overridden image, if True keep processing this one we're at
    }
    """
    def resize_to_resolution(self, **kwargs) -> None:
        # Get the image to process and resize it
        processing = self._get_processing_image(
            kwargs.get("from_current_frame", True)
        )

        w, h = int(kwargs["width"]), int(kwargs["height"])

        # Resize it
        self.image = processing.resize(
            width = w,
            height = h,
        )

        # Override or not, update resolution as this is a resize function
        self._override(kwargs.get("override", False))
        # self._update_resolution()
        self.width, self.height = w, h
    
    # Rotate this frame by a certain angle
    # [ WARNING ] Better only to rotate square images
    def rotate(self,
            angle: float,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        processing = Image.fromarray(self._get_processing_image(from_current_frame).toarray())
        processing = np.asarray(processing.rotate(angle, resample=Image.BICUBIC))

        self.image = skia.Image.fromarray(processing)

        self._override(override)

    # Multiply this image's frame alpha channel by that scalar
    # @ratio: 0 - 1 values
    def transparency(self,
            ratio: float,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        processing = self._get_processing_image(from_current_frame)

        # Split the original image's channels
        r, g, b, alpha = cv2.split(processing.toarray())

        # Multiply the alpha by that ratio
        alpha = np.array(alpha) * ratio

        # Stack the arrays into a new numpy array "as image"
        self.image = skia.Image.fromarray( (np.dstack((r, g, b, alpha))).astype(np.uint8) )

        self._override(override)

    # Apply vignetting on this image object
    # @x: X coordinate center of the effect
    # @y: Y coordinate center of the effect
    # @deviation_$: sigma of the gaussian kernel
    def vignetting(self,
            x: float,
            y: float,
            deviation_x: float,
            deviation_y: float,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        raise DeprecationWarning("Deprecated function")

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

    