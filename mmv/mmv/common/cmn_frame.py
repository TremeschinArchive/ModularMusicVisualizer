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

from mmv.common.cmn_types import *
from glitch_this import ImageGlitcher
from PIL import ImageFilter
from PIL import Image
import numpy as np
import numpy
import time
import copy
import sys
import cv2
import os

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
        self.glitcher = ImageGlitcher()
    
    # # Internal functions
    
    # if override: self.original_image <-- self.image
    def _override(self, override: bool) -> None:
        if override:
            self.original_image = copy.deepcopy(self.image)
    
    # self.frame --> self.image
    def _update_image_from_array(self) -> None:
        self.image = Image.fromarray(self.array)

    # self.image --> self.array
    def _update_array_from_image(self) -> None:
        self.array = np.array(self.image)
    
    # Update resolution from the array shape
    def _update_resolution(self) -> None:
        self.height = self.array.shape[0]
        self.width = self.array.shape[1]

    # self.image = self.original_image
    def _reset_to_original_image(self) -> None:
        if hasattr(self, 'original_image'):
            self.image = copy.deepcopy(self.original_image)
    
    # Get the image we're process the effects on
    def _get_processing_image(self, from_current_frame: bool=False) -> Image:
        if from_current_frame:
            if hasattr(self, 'image'):
                return self.image
            else:
                return Image.fromarray(self.array)
        else:
            return self.original_image

    # # User functions

    # Create new numpy array as a "frame", attribute width, height and resolution
    def new(self, width: Number, height: Number, transparent: bool=False) -> None:

        # Transparent is RGBA, not transparent is RGB
        if transparent:
            channels = 4
        else:
            channels = 3
        
        # Blank zeros frame based on transparency option
        self.array = np.zeros([height, width, channels], dtype=np.uint8)

        # This is our "loaded" image, as we're creating a new, it's the original one
        self.original_image = Image.fromarray(self.array)

        # Update width, height info
        self.width = width
        self.height = height

    # Load this image by array
    def load_from_array(self, array: np.ndarray, convert_to_png: bool=False) -> None:
        # Load the array as image and set it as the frame
        self.original_image = Image.fromarray(array)

        # Alpha composite only works on RGBA if we're going to do it
        if convert_to_png:
            self.original_image = self.original_image.convert("RGBA")

        # Set the image
        self.image = self.original_image
        self.array = array

        # Update width, height info
        self.height = array.shape[0]
        self.width = array.shape[1]

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
                self.original_image = Image.open(path)
                break # the while loop
            except Exception:
                pass
            time.sleep(0.1)

        # Warn the use rwe're not stuck anymore        
        if tries > 10:
            print(debug_prefix, "Could read image from path [%s]" % path)

        # Sometimes we load a background in jpeg and have to process alpha composite
        if convert_to_png:
            self.original_image = self.original_image.convert("RGBA")
        
        # Copy the original image PIL's Image class and sets the frame
        self.image = copy.deepcopy(self.original_image)
        self.array = np.array(self.image)

        # Update width, height info
        self.height = self.image.size[0]
        self.width = self.image.size[1]

    # Get PIL image array from this object frame
    def get_pil_image(self) -> Image:
        return Image.fromarray(self.array.astype(np.uint8))
    
    def get_rgb_frame_array(self) -> np.ndarray:
        return np.array( self.get_pil_image().convert("RGB") )

    # Save an image with specific instructions depending on it's extension type.
    def save(self, directory: str) -> None:

        debug_prefix = "[Frame.save]"

        print(debug_prefix, "Saving to file: [%s]" % directory)

        # JPG and PNG uses different arguments
        if '.jpg' in directory:
            self.get_pil_image().save(directory, format='JPEG', subsampling=0, quality=100)

        elif ".png" in directory:
            self.get_pil_image().save(directory, format='PNG')
    
    # Resize this frame multiplied by a scalar
    #
    # @ratio: scalar to multiply
    # @override: set the original image to the new resized one
    # @from_current_frame: resize not the original image but the current self.array, overrided by override
    #
    # Returns: offset array because of the resized new width and height according to the top left corner
    def resize_by_ratio(self,
            ratio: Number,
            get_only_offset: bool=False,
            override: bool=False,
            from_current_frame: bool=False
        ) -> list:  # Returns the offset because the resize

        debug_prefix = "[Frame.resize_by_ratio]"

        # Calculate the new width and height
        new_width = int(self.width * ratio)
        new_height = int(self.height * ratio)

        # Already on resolution
        if (new_width == self.width) and (new_height == self.height):
            return [0, 0]

        if not get_only_offset:
            
            processing = self._get_processing_image(from_current_frame)
            processing = processing.resize((new_width, new_height), Image.BICUBIC)

            self.image = processing

            self._override(override)
            self._update_array_from_image()
            self._update_resolution()

        # Return the offset to preserve the center
        return [
            (self.width - new_width)/2,
            (self.height - new_height)/2
        ]

    # Resize this frame to a fixed resolution
    # @override: set the original image to the new resized one
    def resize_to_resolution(self,
            width: Number,
            height: Number,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        processing = self._get_processing_image(from_current_frame)
        processing = processing.resize((width, height), Image.BICUBIC)

        self.image = processing

        self._override(override)
        self._update_array_from_image()
        self._update_resolution()
    
    # Rotate this frame by a certain angle
    # [ WARNING ] Better only to rotate square images
    # @override: set the original image to the new rotated
    def rotate(self,
            angle: Number,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        processing = self._get_processing_image(from_current_frame)
        processing = processing.rotate(angle, resample=Image.BICUBIC)

        self.image = processing

        self._override(override)
        self._update_array_from_image()
    
    # Apply gaussian blur to the image by a certain radius
    def gaussian_blur(self,
            radius: Number,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:
        
        processing = self._get_processing_image(from_current_frame)
        processing = processing.filter(ImageFilter.GaussianBlur(radius=radius))

        self.image = processing

        self._override(override)
        self._update_array_from_image()

    # Uses glitch-this
    def glitch(self,
            glitch_amount: Number,
            color_offset: bool=False,
            scan_lines: bool=False
        ) -> None:

        processing = self._get_processing_image(from_current_frame)
        
        # Split the original image's channels
        r, g, b, alpha = processing.split()

        glitched = np.array(
            self.glitcher.glitch_image(
                Image.fromarray(processing),
                round(glitch_amount, 2),
                color_offset=color_offset,
                scan_lines=scan_lines
            )
        )

        # Split the original image's channels
        r, g, b = processing.split()

        # Stack the arrays into a new numpy array "as image"
        self.image = Image.fromarray( (np.dstack((r, g, b, alpha))).astype(np.uint8)) 

        self._override(override)
        self._update_array_from_image()

    # Multiply this image's frame alpha channel by that scalar
    # @ratio: 0 - 1 values
    def transparency(self,
            ratio: Number,
            override: bool=False,
            from_current_frame: bool=False
        ) -> None:

        processing = self._get_processing_image(from_current_frame)

        # Split the original image's channels
        r, g, b, alpha = processing.split()

        # Multiply the alpha by that ratio
        alpha = np.array(alpha) * ratio

        # Stack the arrays into a new numpy array "as image"
        self.image = Image.fromarray( (np.dstack((r, g, b, alpha))).astype(np.uint8) )

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

        processing = self._get_processing_image(from_current_frame)
        
        # Split the image into the channels
        red, green, blue, alpha = processing.split()

        # Get the rows and columns of the image
        img = np.array(self.original_image)
        rows, cols = img.shape[:2]

        # Calculate our mask
        a = cv2.getGaussianKernel(2*cols, deviation_x)[cols - x:2 * cols - x]
        b = cv2.getGaussianKernel(2*rows, deviation_y)[rows - y:2 * rows - y]
        c = b*a.T
        d = c/c.max()

        # Multiply the channels by the mask
        red = red * d
        green = green * d
        blue = blue * d

        # Stack the arrays into a new numpy array "as image"
        self.image = Image.fromarray( (np.dstack((red, green, blue, alpha))).astype(np.uint8) )

        self._override(override)
        self._update_array_from_image()

    #
    # https://stackoverflow.com/questions/52702809/copy-array-into-part-of-another-array-in-numpy
    #
    # Heavily modified, implemented out of bounds safety (a huge headache and pain that took 5+ hours)
    # Remember, numpy's images arrays and coordinates are the following:
    #   - Center point (0, 0) at the top left corner
    #     - X increases to the right
    #     - Y increases downwards
    #   - On reffering, Y is first then X
    #     eg. the rectangular coordinate point (3, -4) is (4, 3) here (Y signal flipped)
    #                                                                                       ~ Have fun
    def copy_from(self,
            A: numpy.ndarray,
            B: numpy.ndarray,
            A_start: list,
            B_start: list,
            B_end: list,
            out_of_bounds_failsafe: bool=True
        ) -> None:

        """
        A_start is the index with respect to A of the upper left corner of the overlap
        B_start is the index with respect to B of the upper left corner of the overlap
        B_end is the index of with respect to B of the lower right corner of the overlap
        """

        debug_prefix = "[Frame.copy_from]"

        # Map the lists as numpy arrays
        A_start, B_start, B_end = map(np.asarray, [A_start, B_start, B_end])

        # The shape of the copying-to coordinates
        shape = B_end - B_start
        resolution = B.shape

        # [ CAUTION ] If we are sure we won't be missing on arguments, this out of bounds
        # failsafe isn't required, make sure you don't need it when not failsafing, that is
        # you agree to only copy_from the inbounds area of this object's self.array
        if out_of_bounds_failsafe:

            # If B_start is before zero, A_start is that offset and B_start is zero,
            # the image is in negative coordinates for example at the top left's (-1, -1)
            for i in range(2):
                if B_start[i] < 0:
                    A_start[i] = - B_start[i]
                    B_start[i] = 0

            # [ NOTE ] Ignore negative shapes, error (?)
            if any([shape[i] < 0 for i in range(2)]):
                return

            # [ Out of Bounds ] We offsetted A_start if B_start is before zero
            # so if the size of the shape is entirely out of bounds
            if A_start[0] >= shape[0] or A_start[1] >= shape[1]:
                return

            # [ Out of Bounds ] B_start is bigger than the B's resolution on that axis
            if B_start[0] >= resolution[0] or B_start[1] >= resolution[1]:
                return

            # # Bottom and right edge out of bounds

            # End is bigger than resolution TODO: does this matter?
            # for i in range(2):
            #     if B_end[i] >= resolution[i]:
            #         B_end[i] = resolution[i] - 1
                    
            # [ Potential error ] Start + shape is bigger than resolution
            for i in range(2):
                if B_start[i] + shape[i] > resolution[i]:
                    B_end[i] = resolution[i] - 1

            # [ FIX ] Shape is bigger than resolution, cut it
            if any([shape[i] >= resolution[i] for i in range(2)]):
                
                # Set the end to the resolution's end
                for i in range(2):
                    B_end[i] = resolution[i]

                # Cut the shape to the minimum of the resolution or its starting point plus the shape
                cut = [
                    min(resolution[0], B_start[0] + shape[0] + 1),
                    min(resolution[1], B_start[1] + shape[1] + 1)
                ]

                # The point we're cutting needs to be offsetted by the starting point
                cut[0] += A_start[0]
                cut[1] += A_start[1]

                # Actually cut A, our insertion image
                A = A[
                    0:cut[0],
                    0:cut[1]
                ]

            # Recalculate the shape if it has changed        
            shape = B_end - B_start

        # Catch any potential error with the transformations on the coordinates      
        try:
            # Get a substitution tuple of the slices
            B_slices = tuple(map(slice, B_start, B_end + 1))
            A_slices = tuple(map(slice, A_start, A_start + shape + 1))

            # Actually make the substitution
            B[B_slices] = A[A_slices]

            # print(debug_prefix, "Copied from, args = {%s, %s, %s}" % (A_start, B_start, B_end))

        except ValueError as e:
            print(debug_prefix, "Fatal error copying block: ", e)
            sys.exit(-1)

    # Same as .copy_from but make an alpha composite on that point
    def overlay_transparent(self,
            overlay: numpy.ndarray,
            x: Number,
            y: Number
        ) -> None:

        """
        We crop this object's frame to the same size as the overlay then make an alpha composite
        with both as PIL only makes this function with two full Image classes, this is a huge
        optimization when looking in the context of particles, in the past we used to make a frame
        the size of this frame's and make an alpha composite the resolution of the entire video every time
        we wanted to process a single particle, it yielded less than 2 frames per second processing time
        """
        
        # [ Out of Bounds ]
        if y >= self.array.shape[0]:
            return
        if x >= self.array.shape[1]:
            return

        # Offset of the cut if X or Y coordinate is negative
        x_offset = 0
        y_offset = 0

        # If any are negative, set it to zero as we can't (we can but it'll get the last item)
        # crop a list this way
        if x < 0:
            x_offset = -x
            x = 0
        if y < 0:
            y_offset = -y
            y = 0
        
        # [ Out of Bounds ] Negative x or y bigger than shape
        if x_offset >= overlay.shape[1]:
            return
        if y_offset >= overlay.shape[0]:
            return

        # The cut position is this coordinate minus the negative offset plus the shape size on that coordinate
        cut_pos = [
            y + overlay.shape[0] - y_offset - 1,
            x + overlay.shape[1] - x_offset - 1
        ]

        # The actual cut is made but we have to limit it to the background size if this cut pos is bigger
        cut = [
            min(cut_pos[0], self.array.shape[0] - 1),
            min(cut_pos[1], self.array.shape[1] - 1)
        ]

        # Crop the frame
        # NOTE: This is simply the coordinate until the cut
        crop = self.array[
            y:cut[0],
            x:cut[1],
        ]

        # Crop the overlay
        # NOTE: This is not as simple as the frame crop as we have a offset we have to add on BOTH 
        # cut indexes according to the actual cut and that is also subtracting the Y and X coordinates
        # offset.
        # Please mediate and have a good imagination on this step as it's hard to explain on words
        overlay = overlay[
            y_offset:cut[0] - y + y_offset,
            x_offset:cut[1] - x + x_offset,
        ]
        
        # Calculate the alpha composite and get its array frame
        alpha_composite = Image.alpha_composite(Image.fromarray(crop), Image.fromarray(overlay))
        alpha_composite = np.array(alpha_composite)

        # Insert out alpha composite-d image to the original place on this object's frame
        self.copy_from(
            alpha_composite,
            self.array,
            [0, 0],
            [y, x],
            [y + crop.shape[0] - 1, x + crop.shape[1] - 1]
        )

        # oof that was a lot

    

    def resolve_pending(self) -> None:

        keys = list(self.pending.keys())

        if "visualizer" in keys:

            module = self.pending["visualizer"]

            visualizer = module[0]
            fftinfo = module[1]

            self.load_from_array(
                visualizer.next(fftinfo),
                convert_to_png=True,
            )

        if "video" in keys:

            module = self.pending["video"]

            frame = module[0]
            width = module[1]
            height = module[2]

            self.load_from_array(frame, convert_to_png=True)
            self.resize_to_resolution(
                width, height,
                override=True,
                from_current_frame=True
            )
        
        if "rotate" in keys:
            module = self.pending["rotate"]
            angle = module[0]
            self.rotate(
                angle,
                from_current_frame=True
            )
        
        if "resize" in keys:
            module = self.pending["resize"]
            ratio = module[0]
            if not self.size == ratio:
                self.resize_by_ratio(
                    ratio,
                    from_current_frame=True
                )
                self.size = ratio
            
        if "blur" in keys:
            module = self.pending["blur"]
            amount = module[0]
            self.gaussian_blur(
                amount,
                from_current_frame=True
            )
        
        if "glitch" in keys:
            module = self.pending["glitch"]
            amount = module[0]
            color_offset = module[1]
            scan_lines = module[2]
            print("glitch", module)
            self.glitch(
                glitch_amount=amount,
                color_offset=color_offset,
                scan_lines=scan_lines,
                from_current_frame=True
            )
        
        if "transparency" in keys:
            module = self.pending["transparency"]
            amount = module[0]
            self.transparency(
                amount,
                from_current_frame=True
            )
        
        # ~ 0.23 seconds on 720p image
        if "vignetting" in keys:

            module = self.pending["vignetting"]

            x = module[0]
            y = module[1]
            value_x = module[2]
            value_y = module[3]

            self.vignetting(
                x, y,
                value_x,
                value_y,
                from_current_frame=True
            )