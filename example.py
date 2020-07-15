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
processing = mmv.mmv()

# Single thread render the video or multiprocessed with N workers?
# Not setting the workers --> defaults to CPU thread count
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
# But we'll add a shake modifier to it by that ammount of pixels on each direction
# So we have to over resize a bit the background so the shake doesn't make black borders
# And start it shake ammounts off the screen
shake = 20
background.configure.resize_to_video_resolution(
    over_resize_x = 2*shake,
    over_resize_y = 2*shake,
)

# Set the object fixed point position off screen
background.configure.add_path_point(-shake, -shake)

# Shake by "shake" ammount of pixels at max on any direction
background.configure.simple_add_path_modifier_shake(shake)

# Blur the background when the average audio amplitude increases
background.configure.simple_add_linear_blur(intensity="medium")

# Resize the background when the average audio amplitude increases
background.configure.simple_add_linear_resize(intensity="high")

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
logo.configure.load_image("assets/tremx_assets/logo/logo.png")
logo.configure.resize_to_resolution(logo_size, logo_size, override=True)

# The starting point is a bit hard to understand, we want to center it but have to
# account the logo size, so the first part gets the center point of the resolution
# and the second part subtracts half the logo size on each Y and X direction
logo.configure.add_path_point(
    (processing.width // 2) - (logo_size/2),
    (processing.height // 2) - (logo_size/2),
)

logo.configure.simple_add_linear_resize(intensity="custom", activation="1+7*X")

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
    responsiveness=0.25,
    pre_fft_smoothing=2,
    pos_fft_smoothing=0,
    subdivide=0
)

# Center the visualizer
visualizer.configure.add_path_point(
    processing.width // 2 - (visualizer_size / 2),
    processing.height // 2 - (visualizer_size / 2),
)

# visualizer.configure.simple_add_linear_blur(intensity="high")
visualizer.configure.simple_add_linear_resize(intensity="custom", activation="1+8*X")

# # We can define how much shake we want
# visualizer.configure.simple_add_path_modifier_shake(
#     shake_max_distance=5,
#     x_smoothness=0.01,
#     y_smoothness=0.02
# )

processing.add(visualizer, layer=3)

# Run and generate the final video
processing.run()
