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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH, STEP_SEPARATOR
from PIL import Image
import numpy as np
import logging
import sys
import os


class MMVShaderMaker:
    def __init__(self, mmvshader_main):
        debug_prefix = "[MMVShaderMaker.__init__]"
        self.mmvshader_main = mmvshader_main
        
    # # Internal functions
    
    # Converts an numpy array into a sequence of hexadecimal raw pixel values
    # Used when defining TEXTURES on mpv shaders
    def __np_array_to_uint8_hex(self, array):
        return array.astype(np.uint8).tobytes().hex().upper()

    # Loads an image from path and converts to raw hexadecimal rgba pixels
    def __image2hex_rgba8(self, image):
        return self.__np_array_to_uint8_hex(np.array(image))

    # Read a template shader from the input path, replaces values in between <++>
    # then saves to runtime dir, returns the path of the new shader
    def replaced_values_shader(self, input_shader_path, depth = LOG_NO_DEPTH, **values) -> str:  # -> Path
        debug_prefix = "[MMVShaderMaker.replaced_values_shader]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        # logging.debug(f"{depth}{debug_prefix} Replacing values on shader [{input_shader_path}], values: {values}")

        # Received keys
        keys = [key for key in values.keys()]
        logging.info(f"{depth}{debug_prefix} Received substitution keys from user: {keys}")

        # Activation for changing the amount on the shader itself
        if not "activation" in keys:
            logging.warn(f"{depth}{debug_prefix} Setting no activation for this shader")
            values["activation"] = "// amount = amount"
        
        # What values we'll iterate over and over the shader for changing the amount
        # one changing_amount with one item means it is constant, alternatively you
        # can send a "constant_amount"
        if not "changing_amount" in keys:
            logging.warn(f"{depth}{debug_prefix} changing_amount key not in substitution keys, checking for regular \"amount\" key")

            # User didn't gave much information (no array nor constant amount)
            if not "constant_amount" in keys:
                logging.critical(f"{depth}{debug_prefix} Didn't set changing_amount nor constant_amount")
                sys.exit(-1)

            logging.info(f"{depth}{debug_prefix} Assigning values[\"changing_amount\"] = [values[\"constant_amount\"]]")
            values["changing_amount"] = [values["constant_amount"]]

        # Set number of amount values to the len of the array
        logging.info(f"{depth}{debug_prefix} Setting up default substitution [number_of_amount_values] -> [len(values[\"changing_amount\"])]")
        values["number_of_amount_values"] = len(values["changing_amount"])

        # Load the raw string of the shader
        with open(input_shader_path, "r") as shader:
            shader_data = shader.read()

        # Get unique ID for saving on the runtime directory
        unique_id = self.mmvshader_main.utils.get_unique_id(f"Shader at [{input_shader_path}]", depth = ndepth)

        # Iterate on the dictionary the user sent us
        for key, value in values.items():

            # If elses are 1 an 0
            if value == True:
                value = "1"
            elif value == False:
                value = "0"

            # Convert a list to a string of a, b, c, d, e, f be sure to remove the last ,
            if isinstance(value, list):
                to_c_array = ""
                for number in value:
                    to_c_array += f"{str(number)},"
                value = to_c_array[:-1]

            # Log what we are changing
            # logging.info(f"{depth}{debug_prefix} Replacing [{key}] -> [{value}] in shader")

            # How many times this will be substituted?
            occurrences = shader_data.count(key)
            
            # Warn how many times this was found, if it's zero then it doesn't exist / typo?
            logging.debug(f"{depth}{debug_prefix} Occurrences of the key [{key}] in shader: [{occurrences}]")

            # Warn zero occurrences
            if occurrences == 0:
                logging.warn(f"{depth}{debug_prefix} No occurences of key [{key}] on shader at [{input_shader_path}], typo or intended?")

            # Replace the 
            shader_data = shader_data.replace(f"<+{key}+>", str(value))
        
        # Get the filename of the original shader
        original_shader_filename = self.mmvshader_main.utils.get_filename_no_extension(input_shader_path, depth = ndepth)

        # Where to save this replaced shader
        runtime_shader_file_path = f"{self.mmvshader_main.context.directories.runtime}{os.path.sep}{original_shader_filename}-[{unique_id}].glsl"

        # Log where it'll be located
        logging.info(f"{depth}{debug_prefix} Saving replaced runtime shader at [{runtime_shader_file_path}]")

        # Open the file then save it
        with open(runtime_shader_file_path, "w") as new_shader:
            new_shader.write(shader_data)
        
        # Return the new shader path as specified on the function doc
        return runtime_shader_file_path

    # Change values on a generic image shader
    """
    kwargs: {
        "image": Source image
    }
    """
    def generic_image_shader(self, output_path, **kwargs):
        debug_prefix = "[MMVShaderMaker._generic_image_shader]"

        # Get data on the original shader
        with open(f"{self.mmvshader_main.DIR}/glsl/mmv_image_shader_template.glsl", "r") as f:
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