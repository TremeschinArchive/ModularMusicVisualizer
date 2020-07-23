"""
===============================================================================

Purpose: Basic usage example of using PyGradienter on MMV, for creating
unique and free to use assets / images on MMV videos

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

import mmv

processing = mmv.mmv()

# Get a pygradienter object
pygradienter = processing.pygradienter(workers=12)

# Set where we'll be saving our assets to
processing.assets_dir("assets/user_assets")

# Set the resolution we want to create the pygradienter images
pygradienter.config.resolution(200, 200)

# How many images we'll be generating
pygradienter.config.n_images(2)

# The pygradienter profile we'll create
profile = "simple_smooth"

# Get the generated images from pygradienter
generated_images = pygradienter.generate(profile)

# Where we'll be saving the generated images on
save_directory = f"{processing.assets_dir}/pygradienter/{profile}"

# Use utils mkdir_dne function ( make directory (if) does not exist ) for saving
processing.utils.mkdir_dne(save_directory) 

# Enumerate through the PNG images we got from pygradienter, that is:
# 
# names = ["John", "Walter", "Camila"]
#
# for index, item in enumerate(names):
#     print(index, item)
# 
# That prints:
# >> 0, "John"
# >> 1, "Walter"
# >> 2, "Camila"
#
for index, image in enumerate(generated_images):
    
    # Get a unique id for the filename
    unique_image_id = processing.get_unique_id()

    save_file_path = f"{save_directory}/{unique_image_id}.png"

    # Save the image to that path
    image.save(save_file_path)
