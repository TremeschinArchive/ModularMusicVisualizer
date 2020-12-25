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

# Import modules
import mmv
import os

# Start and get shader interface, assign mpv var to
# a shorthand for accessing MMVShaderMPV class
interface = mmv.MMVInterface()
processing = interface.get_shader_interface()
mpv = processing.mmv_shader_main.mpv

# Where this insterface is located
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# If you set an output video it'll render to a file.
# Only works on Linux, Windows you can only visualize
# I have no control over this since it's an mpv feature.
# For more info, set output video on Windows and run this script.
mpv.input_output(
    input_video = f"{THIS_DIR}/shy-piano.mkv",
    output_video = "out.mp4"
)

# Target render resolution, won't be applied
# if you only visualize the video
mpv.resolution(width = 1280, height = 720)

# # For now comment / uncomment the shaders you want to apply

# mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/r1_grayscale.glsl")
# mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/r1_bitcrush.glsl")
# mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/r1_chromatic_aberration.glsl")
mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/r1_vignetting.glsl")
mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/r1_edge_saturation_low.glsl")
mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/wip_test_sphere.glsl")
mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/r1_tsubaup.glsl")
mpv.add_shader(f"{processing.MMV_SHADER_ROOT}/glsl/wip_adaptive-sharpen.glsl")

# Ignore, testing
# texture_shader_test_path = f"{mmv.context.directories.runtime}/test_texture.glsl"
# mmv.shader_maker.generic_image_shader(
#     output_path = texture_shader_test_path,
#     image = f"{THIS_DIR}/../repo/mmv-project-logo.png"
# )
# mpv.add_shader(texture_shader_test_path)

# Run!
mpv.run()
