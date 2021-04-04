"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Generate BlocksOfCode

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
from mmv.common.cmn_utils import Utils
import logging


class MMVShaderMakerTransformations:
    def __init__(self):
        self.utils = Utils()
    
    # Blit some image at some x, y at certain scale, angle, etc.
    def image(self,
        image, assign_to_variable = "layered", new_variable = True,
        x = 0, y = 0, scale = 1.0, angle = 0,
        canvas = "layered", uv = "stuv", anchor = "vec2(0.5, 0.5)",
        shift = "vec2(0.5, 0.5)", repeat = False,
        undo_gamma = True, gamma = 2.0, **kwargs
    ):
        debug_prefix = "[MMVShaderMakerTransformations.image]"

        new = "vec4 " if new_variable else ""
        repeat = self.utils.bool_to_string(repeat)
        undo_gamma = self.utils.bool_to_string(undo_gamma)

        boc = BlockOfCode((
            f"{new}{assign_to_variable} = mmv_blit_image(\n"
            f"    {canvas}, // Canvas\n"
            f"    {image}, // Image\n"
            f"    {image}_resolution, // Resolution\n"
            f"    {uv}, // UV\n"
            f"    {anchor}, // Anchor\n"
            f"    {shift}, // Shift\n"
            f"    {scale}, // Scale\n"
            f"    {angle}, // Angle\n"
            f"    {repeat}, // Repeat\n"
            f"    {undo_gamma}, // Undo gamma\n"
            f"    {gamma} // Gamma\n"
            f")"
        ), scoped = kwargs.get("scoped", True))

        logging.info(f"{debug_prefix} Returning BlockOfCode:")
        for line in boc.get_content(): logging.info(f"{debug_prefix} | {line}")
        return boc

    def get_texture(self, texture_name, uv = "stuv", assign_to_variable = "processing", new_variable = True, **kwargs):
        debug_prefix = "[MMVShaderMakerTransformations.get_texture]"

        new = "vec4 " if new_variable else ""
        boc = BlockOfCode((
            f"{new}{assign_to_variable} = texture({texture_name}, {uv});"
        ), scoped = kwargs.get("scoped", True))
        logging.info(f"{debug_prefix} Returning BlockOfCode:")
        for line in boc.get_content(): logging.info(f"{debug_prefix} | {line}")
        return boc

    # Alpha
    def alpha_composite(self, new, old = "layered", **kwargs):
        debug_prefix = "[MMVShaderMakerTransformations.alpha_composite]"

        boc = BlockOfCode((
            f"layered = mmv_alpha_composite({new}, {old});"
        ), scoped = kwargs.get("scoped", False))
        logging.info(f"{debug_prefix} Returning BlockOfCode:")
        for line in boc.get_content(): logging.info(f"{debug_prefix} | {line}")
        return boc
    
    def gamma_correction(self, exponent = 2.0, **kwargs):
        debug_prefix = "[MMVShaderMakerTransformations.gamma_coorection]"

        boc = BlockOfCode((
            f"layered = pow(layered, vec4(1.0 / {exponent}));"
        ), scoped = kwargs.get("scoped", False))
        logging.info(f"{debug_prefix} Returning BlockOfCode:")
        for line in boc.get_content(): logging.info(f"{debug_prefix} | {line}")
        return boc
    
    def fade_in(self, formula = "(atan(mmv_time*mmv_time)*2) / 3.141596", stop_after = 10):
        debug_prefix = "[MMVShaderMakerTransformations.fade_in]"
        boc = BlockOfCode((
            f"if (mmv_time < {stop_after}) {{\n"
            f"    float fadein = {formula};\n"
            f"    layered = fadein * layered;\n"
            f"}}"
        ), scoped = True)
        logging.info(f"{debug_prefix} Returning BlockOfCode:")
        for line in boc.get_content(): logging.info(f"{debug_prefix} | {line}")
        return boc
