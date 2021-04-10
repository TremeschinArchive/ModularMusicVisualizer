"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Some stuff can get quite repetitive with MMVShaderMaker, here lies
some macros such as alpha compositing N-amount of shaders and get something
with everything mapped accordingly

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
from mmv.mmvshader.abstractions.abstraction_block_of_code import BlockOfCode
import logging
import uuid


class MMVShaderMakerMacros:
    def __init__(self, mmv_shader_maker):
        
        # Get master class
        self.mmv_shader_maker = mmv_shader_maker
        self.transformations = self.mmv_shader_maker.transformations
    
    # Loads shader from path
    def load(self, path, get_name_from_file = True):
        processing = self.mmv_shader_maker.clone()
        processing.load_shader_from_path(path = path, get_name_from_file = get_name_from_file)
        return processing

    # Map shader A as "layer" sampler2D on shader B
    def chain(self, A, B):
        B.add_dynamic_shader_mapping(name = "layer", fragment_shader_path = A.finish())
        return B

    # Alpha composite many layers automatically like magic!
    def alpha_composite(self, layers: list, finish = False):
        debug_prefix = "[MMVShaderMakerMacros.alpha_composite]"
        concatenated = self.mmv_shader_maker.clone()
        concatenated.set_name(f"shader_maker_macro_alpha_composite_master_shader_{str(uuid.uuid4())[:6]}")
        concatenated.add_include("mmv_specification")

        # Iterate on layers
        for index, layer in enumerate(layers):
            layer_name = f"layer{index}"

            # Construct final shader, get final path
            path = layer.finish()

            # Add mapping
            concatenated.add_dynamic_shader_mapping(name = layer_name, fragment_shader_path = path)

            # Alpha Composite variable name
            AC = f"alpha_composite_{layer_name}"

            # Get texture from the shader
            processing = concatenated.transformations.get_texture(
                texture_name = layer_name,
                uv = "shadertoy_uv",
                assign_to_variable = AC
            )

            # Extend alpha composite on AC variable
            processing.extend(concatenated.transformations.alpha_composite(new = AC))

            # Add transformation
            concatenated.add_transformation(transformation = processing)
        
        # Return the final shader
        if finish:
            return concatenated.finish()
        else:
            return concatenated