"""
===============================================================================

Purpose: Basic usage example of MMV

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

"""
# # # [ IMPORTANT ] # # #

When setting coordinates like path points, the reference is the following:

Center (0, 0) is at the top left corner of the video,
and the "object" position is at the top left corner of its image as well

X increases rightwards
Y increases downwards
"""

# Import MMV module
import mmv

# Create the wrapper class
processing = mmv.mmv(
    watch_processing_video_realtime=False
)

# Single thread render the video or multiprocessed with N workers?
# Not setting the workers --> defaults to 4
processing.performance(
    multiprocessed=True,
    workers=4
)

# Set the video quality
processing.quality(
    width=1280,
    height=720,
    fps=60
)

# We can also set by a preset like so
# processing.quality_preset.fullhd60()

# The way we process and get the frequencies from the audio, highly
# influences the frequencies bars on the visualizer itself
processing.audio_processing.preset_bass_mid()

# # #
 
# If you want to create some assets, set the assets dir first !!
processing.assets_dir("assets/free_assets")

# Pygradienter assets only works on Linux at the moment :(
# processing.create_pygradienter_asset(
#     profile="particles",
#     width=150, height=150,
#     n=20, delete_existing_files=True
# )

# # #

# I/O options, input a audio, output a video
processing.input_audio("assets/free_assets/sound/banjo.ogg")
processing.output_video("mmv-output.mkv")

# # # Background

# Get an MMV image object
background = processing.image_object()

# Initialize this animation layer, we're at layer 0
background.configure.init_animation_layer()

# We can load an random image from the dir :)
background.configure.load_image(
    processing.random_file_from_dir("assets/free_assets/background/simple-smooth")
)

# As the background fills the video, we resize it to the video resolution
# But we'll add a shake modifier to it by that amount of pixels on each direction
# So we have to over resize a bit the background so the shake doesn't make black borders
# And start it shake amounts off the screen
shake = 20
background.configure.resize_to_video_resolution(
    over_resize_x = 2*shake,
    over_resize_y = 2*shake,
)

# Set the object fixed point position off screen
background.configure.add_path_point(-shake, -shake)

# Shake by "shake" amount of pixels at max on any direction
background.configure.simple_add_path_modifier_shake(shake)

# Blur the background when the average audio amplitude increases
background.configure.simple_add_linear_blur(intensity="medium")

# Resize the background when the average audio amplitude increases
background.configure.simple_add_scalar_resize(intensity="high")

# Add the backround object to be generated
# The layers are a ascending order of blitted items, 0 is first, 1 is after zero
# So our background is before everything, layer 0
processing.add(background, layer=0)

# # # Logo

# Our logo size, it's a good thing to keep it proportional according to the resolution
# so I set it to a 200/720 proportion on a HD 720p resolution, but I have to multiply by
# the new resolution afterwards
logo_size = (200/720)*processing.height

logo = processing.image_object()
logo.configure.init_animation_layer()
logo.configure.load_image("assets/free_assets/mmv-logo.png")
logo.configure.resize_to_resolution(logo_size, logo_size, override=True)

# The starting point is a bit hard to understand, we want to center it but have to
# account the logo size, so the first part gets the center point of the resolution
# and the second part subtracts half the logo size on each Y and X direction
logo.configure.add_path_point(
    (processing.width // 2) - (logo_size/2),
    (processing.height // 2) - (logo_size/2),
)

logo.configure.simple_add_scalar_resize(intensity="high")

# We can add rotation to the object
logo.configure.simple_add_swing_rotation()

processing.add(logo, layer=4)

# Create a visualizer object, see [TODO] wiki for more information
visualizer = processing.image_object()
visualizer.configure.init_animation_layer()
visualizer_size = min(processing.resolution)
visualizer.configure.simple_add_visualizer_circle(
    width=visualizer_size, height=visualizer_size,
    minimum_bar_size=logo_size//2,
    mode="symetric",
    responsiveness=0.6,
    pre_fft_smoothing=0,
    pos_fft_smoothing=0,
    subdivide=6
)

# Center the visualizer
visualizer.configure.add_path_point(
    processing.width // 2 - (visualizer_size / 2),
    processing.height // 2 - (visualizer_size / 2),
)

# visualizer.configure.simple_add_linear_blur(intensity="high")
visualizer.configure.simple_add_scalar_resize(
    intensity="high-plus", # A bit more than the high setting
)

# # We can define how much shake we want
# visualizer.configure.simple_add_path_modifier_shake(
#     shake_max_distance=5,
#     x_smoothness=0.01,
#     y_smoothness=0.02
# )

processing.add(visualizer, layer=3)

# # Post processing / effects

generator = processing.generator_object()
generator.particle_generator()
generator.generator.configure.preset_bottom_mid_top()

processing.add(generator)

# Add simple vignetting on default configs on the post processing
# Those darken the edges of the screen when the average amplitude of the audio
# goes up, mostly with the bass. Search for vignetting, you'll see what I mean
processing.post_processing.simple_add_vignetting()


# Run and generate the final video
processing.run()
