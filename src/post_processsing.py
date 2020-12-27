"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

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

# Aliases for faster accessing functions
mpv = processing.mmv_shader_main.mpv
shader_maker = processing.mmv_shader_main.shader_maker

processing.list_shaders()
if False: exit()  # Change this to True for listing the shaders and their description then quit

# Ensure we have mpv on Windows, downloads, extracts etc
# Does nothing for Linux, make sure you have mpv package installed on your distro
interface.download_check_mpv()

# Where this insterface is located
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sep = os.path.sep

# # What code branch to follow? read lasT_session_info.toml or custon

POST_PROCESS_TYPE = "last_render"
# POST_PROCESS_TYPE = "custom"


# If set to False will play real time
# Rendering to video is a Linux only feature, not available due MPV limitations on Windows and macOS
RENDER_TO_VIDEO = False
OUTPUT_VIDEO_NAME = f"{THIS_DIR}{sep}post_process_output.mkv"


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


# Micro managing
if RENDER_TO_VIDEO:
    output_video = OUTPUT_VIDEO_NAME
else:
    output_video = None

# Grab info on the last rendered video and pass it through here
if POST_PROCESS_TYPE == "last_render":

    # Last session info file doesn't exist, error and quit
    if not os.path.exists(interface.last_session_info_file):
        raise RuntimeError(f"Could not find last_session_info.toml at path [{interface.last_session_info_file}], did you run MMVSkia (base_video.py) first?")

    # I have no control over this since it's an mpv feature. For more info, set output video on Windows and run this script.
    mpv.input_output(
        input_video = "last_rendered",  # Setting it to "last_rendered" gets the last rendered file from mmvskia
        output_video = output_video
    )

    # Get the last rendered video 
    activation_values = interface.utils.load_toml(
        interface.last_session_info_file
    )["audio_amplitudes"]

    # # Chromatic aberration
    chromatic_aberration_shader = shader_maker.replaced_values_shader(
        input_shader_path = f"{processing.MMV_SHADER_ROOT}/glsl/fx/r1_chromatic_aberration.glsl",
        changing_amount = activation_values,
        activation = "amount = amount * 4.0",
    )  # This .replaced_values_shader returns the path of the replaced shader
    mpv.add_shader(chromatic_aberration_shader)

    # # Edge = low saturation
    edge_low_saturation_shader = shader_maker.replaced_values_shader(
        input_shader_path = f"{processing.MMV_SHADER_ROOT}/glsl/fx/r1_edge_saturation_low.glsl",
        changing_amount = [
            max(2 - (value*5), 0.2) for value in activation_values
        ],
    )  # This .replaced_values_shader returns the path of the replaced shader
    mpv.add_shader(edge_low_saturation_shader)

# Custom processing, TODO: read the 
elif POST_PROCESS_TYPE == "custom":
    mpv.input_output(
        input_video = f"{THIS_DIR}/shy-piano.mkv",
        output_video = output_video
    )
    mpv.resolution(width = 1920, height = 1080)

# Run! (or render)
mpv.run()
