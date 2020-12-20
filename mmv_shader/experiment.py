"""
===============================================================================

Purpose: Developers, developers, developers

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

import mmvshader
import os

mmv = mmvshader.MMVShaderMain()

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

mmv.mpv.input_output(
    input_video = f"{THIS_DIR}/data/source.mkv",
    # output_video = "out.mp4"
)
mmv.mpv.resolution(width = 1280, height = 720)
# mmv.mpv.add_shader(f"{mmv.DIR}/glsl/test_grayscale.glsl")
mmv.mpv.add_shader(f"{mmv.DIR}/glsl/test_bitcrush.glsl")
mmv.mpv.add_shader(f"{mmv.DIR}/glsl/test_chromatic_aberration.glsl")
mmv.mpv.add_shader(f"{mmv.DIR}/glsl/test_vignetting.glsl")

texture_shader_test_path = f"{mmv.context.directories.runtime}/test_texture.glsl"

mmv.maker.generic_image_shader(
    output_path = texture_shader_test_path,
    image = f"{THIS_DIR}/../repo/mmv-project-logo.png"
)

mmv.mpv.add_shader(texture_shader_test_path)


mmv.mpv.run()
