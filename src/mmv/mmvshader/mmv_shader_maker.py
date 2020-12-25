"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Utility to wrap around mpv and add processing shaders, target
resolutions, input / output

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

from PIL import Image
import numpy as np
import os


class MMVShaderMaker:
    def __init__(self, main):
        debug_prefix = "[MMVShaderMaker.__init__]"
        self.mmv_main = main
        
    # # Internal functions
    
    # Converts an numpy array into a sequence of hexadecimal raw pixel values
    # Used when defining TEXTURES on mpv shaders
    def __np_array_to_uint8_hex(self, array):
        return array.astype(np.uint8).tobytes().hex().upper()

    # Loads an image from path and converts to raw hexadecimal rgba pixels
    def __image2hex_rgba8(self, image):
        return self.__np_array_to_uint8_hex(np.array(image))

    # # External but non end user functions

    # Change values on a generic image shader
    """
    kwargs: {
        "image": Source image
    }
    """
    def generic_image_shader(self, output_path, **kwargs):
        debug_prefix = "[MMVShaderMaker._generic_image_shader]"

        # Get data on the original shader
        with open(f"{self.mmv_main.DIR}/glsl/mmv_image_shader_template.glsl", "r") as f:
            shader = f.read()
        
        # # Main routine enabling / configuring stuff

        # Open the source image
        image = Image.open(kwargs["image"]).convert("RGBA")
        width, height = image.size

        # What to replace
        replaces = {
            "<+IMAGEHEX+>": self.__image2hex_rgba8(image),
            "<+IMAGEWIDTH+>": width,
            "<+IMAGEHEIGHT+>": height,
        }

        # Replace each key on that dictionary
        for key, value in replaces.items():
            shader = shader.replace(key, str(value))

        # Write to output shader
        with open(output_path, "w") as f:
            f.write(shader)