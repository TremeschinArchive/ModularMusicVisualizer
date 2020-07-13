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
from mmv.utils import Utils
from PIL import Image
import numpy as np
import numpy
import time
import copy
import sys
import cv2
import os


class Frame():
    def __init__(self):
        self.utils = Utils()

        # Multiprocessing pending things to do, ordered
        self.pending = {}
        self.size = 1

    # Create new numpy array as a "frame", attribute width, height and resolution
    def new(self, width, height, transparent=False):

        # Transparent is RGBA, not transparent is RGB
        if transparent:
            channels = 4
        else:
            channels = 3
        
        # Blank zeros frame based on transparency option
        self.frame = np.zeros([height, width, channels], dtype=np.uint8)

        # This is our "loaded" image, as we're creating a new, it's the original one
        self.original_image = Image.fromarray(self.frame)

        # Update width, height info
        self.width = width
        self.height = height

    # Load this image by array
    def load_from_array(self, array, convert_to_png=False):
        # Load the array as image and set it as the frame
        self.original_image = Image.fromarray(array)

        # Alpha composite only works on RGBA if we're going to do it
        if convert_to_png:
            self.original_image = self.original_image.convert("RGBA")

        # Set the image
        self.image = self.original_image
        self.frame = array

        # Update width, height info
        self.height = array.shape[0]
        self.width = array.shape[1]

    # Load image from a given path
    def load_from_path(self, path, convert_to_png=False):

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
        self.frame = np.array(self.image)

        # Update width, height info
        self.height = self.image.size[0]
        self.width = self.image.size[1]

    # Wait until a file exist and then load it as a image
    def load_from_path_wait(self, path, convert_to_png=False):
        self.utils.until_exist(path)
        self.load_from_path(path, convert_to_png=convert_to_png)

    # Get PIL image array from this object frame
    def image_array(self):
        return Image.fromarray(self.frame.astype(np.uint8))
    
    def get_rgb_frame_array(self):
        return np.array( self.image_array().convert("RGB") )

    # Save an image with specific instructions depending on it's extension type.
    def save(self, directory):

        debug_prefix = "[Frame.save]"

        print(debug_prefix, "Saving to file: [%s]" % directory)

        # JPG and PNG uses different arguments
        if '.jpg' in directory:
            jpegsave = self.image_array()
            jpegsave.save(directory, format='JPEG', subsampling=0, quality=100)

        elif ".png" in directory:
            save_image = self.image_array()
            save_image.save(directory, format='PNG')
    
    # Resize this frame multiplied by a scalar
    # @ratio: scalar to multiply
    # @override: set the original image to the new resized one
    # @from_current_frame: resize not the original image but the current self.frame, overrided by override
    def resize_by_ratio(self, ratio, override=False, from_current_frame=False, get_only_offset=False):

        debug_prefix = "[Frame.resize_by_ratio]"

        # Calculate the new width and height
        new_width = int(self.width * ratio)
        new_height = int(self.height * ratio)

        if not get_only_offset:
            if override:
                # Resize the original image itself and set it as the resized as well as the image var
                self.original_image = self.original_image.resize((new_width, new_height), Image.ANTIALIAS)
                self.image = self.original_image

                # Standart procedure on updating this class info
                self.frame = np.array(self.image)
                self.height = self.frame.shape[0]
                self.width = self.frame.shape[1]

            else:
                # Do we want self.image to be the self.image itself resized or the
                if from_current_frame:
                    toresize = self.image
                else:
                    toresize = self.original_image

                # Resize and update the frame info
                self.image = toresize.resize((new_width, new_height), Image.ANTIALIAS)
                self.frame = np.array(self.image)

        # Return the offset to preserve the center
        return [
            (self.width - new_width)/2,
            (self.height - new_height)/2
        ]
    
    # Resize this frame to a fixed resolution
    # @override: set the original image to the new resized one
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
    
    # Rotate this frame by a certain angle
    # [ WARNING ] Better only to rotate square images
    # @override: set the original image to the new rotated
    def rotate(self, angle, override=False):
        if override:
            self.original_image = self.original_image.rotate(angle, resample=Image.BICUBIC)
            self.image = self.original_image
            self.frame = np.array(self.image)
        else:
            self.image = self.original_image.rotate(angle, resample=Image.BICUBIC)
            self.frame = np.array(self.image)
    
    # Apply gaussian blur to the image by a certain radius
    def gaussian_blur(self, radius):
        self.image = self.image.filter(ImageFilter.GaussianBlur(radius=radius))
        self.frame = np.array(self.image)
    
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
    def copy_from(self, A, B, A_start, B_start, B_end, out_of_bounds_failsafe=True):
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
        # you agree to only copy_from the inbounds area of this object's self.frame
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
    def overlay_transparent(self, overlay, x, y):
        """
        We crop this object's frame to the same size as the overlay then make an alpha composite
        with both as PIL only makes this function with two full Image classes, this is a huge
        optimization when looking in the context of particles, in the past we used to make a frame
        the size of this frame's and make an alpha composite the resolution of the entire video every time
        we wanted to process a single particle, it yielded less than 2 frames per second processing time
        """
        
        # [ Out of Bounds ]
        if y >= self.frame.shape[0]:
            return
        if x >= self.frame.shape[1]:
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
            min(cut_pos[0], self.frame.shape[0] - 1),
            min(cut_pos[1], self.frame.shape[1] - 1)
        ]

        # Crop the frame
        # NOTE: This is simply the coordinate until the cut
        crop = self.frame[
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
            self.frame,
            [0, 0],
            [y, x],
            [y + crop.shape[0] - 1, x + crop.shape[1] - 1]
        )

        # oof that was a lot

    # Multiply this image's frame alpha channel by that scalar
    # @ratio: 0 - 1 values
    def transparency(self, ratio):

        # Split the original image's channels
        r, g, b, alpha = self.original_image.split()

        # Multiply the alpha by that ratio
        alpha = np.array(alpha)*ratio

        # Stack the arrays into a new numpy array "as image"
        image = (np.dstack((r, g, b, alpha))).astype(np.uint8)

        # Load the image from the processed array and attribute the frame to it
        self.image = Image.fromarray(image)
        self.frame = image
    
    # Apply vignetting on this image object
    # @x: X coordinate center of the effect
    # @y: Y coordinate center of the effect
    # @deviation_$: sigma of the gaussian kernel
    def vignetting(self, x, y, deviation_x, deviation_y):

        # Split the image into the channels
        red, green, blue, alpha = self.original_image.split()

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

        # Stack the arrays and build our new image
        image = (np.dstack((red, green, blue, alpha))).astype(np.uint8)

        # Attribute this object frame and image
        self.image = Image.fromarray(image)
        self.frame = image

    def resolve_pending(self):

        keys = list(self.pending.keys())

        if "visualizer" in keys:

            module = self.pending["visualizer"]

            visualizer = module[0]
            fftinfo = module[1]

            self.load_from_array(
                visualizer.next(fftinfo),
                convert_to_png=True
            )

        if "video" in keys:

            module = self.pending["video"]

            frame = module[0]
            width = module[1]
            height = module[2]

            self.load_from_array(frame, convert_to_png=True)
            self.resize_to_resolution(
                width, height,
                override=True
            )
        
        if "rotate" in keys:
            module = self.pending["rotate"]
            angle = module[0]
            self.rotate(angle)
        
        if "resize" in keys:
            module = self.pending["resize"]
            ratio = module[0]
            if not self.size == ratio:
                self.resize_by_ratio(
                    ratio, from_current_frame="rotate" in keys
                )
                self.size = ratio
            
        if "blur" in keys:
            module = self.pending["blur"]
            ammount = module[0]
            self.gaussian_blur(ammount)
        
        if "fade" in keys:
            module = self.pending["fade"]
            ammount = module[0]
            self.transparency(ammount)
        
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
                value_y
            )