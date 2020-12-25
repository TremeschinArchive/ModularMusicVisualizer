"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

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

# # # End user utilities, you can ignore this code

from modules.end_user_utilities import Requirements, ArgParser
import sys

# Parse shell arguments
args = ArgParser(sys.argv)

# We'll automatically install dependencies if we need and user flags so
# Send --auto-deps flag while running this file
if args.auto_deps:
    requirements = Requirements()

    # If we're running from source we have to run it
    if requirements.need_to_run:
        requirements.install()

# # # MMV

# Import MMV module
import mmv

# Import a "canvas" class for generating background image video textures
from mmv.mmvskia.pyskt.pyskt_backend import SkiaNoWindowBackend

# For auto naming files according to when you run MMV
import datetime

# For us to refer relative paths to this example_basic.py
# THIS_FILE_DIR = path directory of where this file is located without the last "/"
# It is assumed this file is under /repository_folder/mmv/example_basic.py so 
# THIS_FILE_DIR is "/repository_folder/mmv"
import os
THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the wrapper class
interface = mmv.MMVInterface()

processing = interface.get_skia_interface(
    # AFAIK skia-python on Linux and MacOS uses RGBA and on Windows BGRA pixel format.
    # "auto" does that, or manually put "rgba" or "bgra". If set wrongly the video
    # colors RED and BLUE will be swapped.
    pixel_format = "auto",

    # If your audio isn't properly normalized or you want a more aggressive video,
    # set this to 1.5 - 2 or so
    audio_amplitude_multiplier = 1,

    # Use or not a GPU accelerated context, pass render=gpu or render=cpu flags
    # For higher resolutions 720p+, GPUs are definitely faster for raw output
    # but for smaller res, CPUs win on image transfering, it defaults to GPU
    # on the final video render if no flag was passed. Generating images such as
    # particles and backgrounds is done on CPU as no textures are being moved.
    render_backend = args.render,
)

# Ensure we have FFmpeg on Windows, downloads, extracts etc
# Does nothing for Linux, make sure you have ffmpeg package installed on your distro
interface.download_check_ffmpeg()

"""
Set the video quality
    batch_size:
        N of the FFT sliced audio, 4096 should be ok, less means less accurate but more responsive
        fft, I'd recommend going 4096*2 for glitch hop or kawaii bass / similar and perhaps
        a lower value for everything else
    width, height:
        Video resolution
    fps:
        Frame rate of the video, animations should scale accordingly
"""
processing.quality(
    width = 1920,
    height = 1080,
    fps = 60,
    batch_size = 4096,
)

# We can also set by a preset like so
# processing.quality_preset.fullhd60()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# We have two main modes "music" and "piano_roll", you can uncomment them

# Default mode
MODE = "music"

# Pass a flag mode=music or mode=piano when calling this script
# if that flag exists, then it overrides that previous MODE
if "mode" in args.kflags:
    if args.kflags["mode"] == "piano":
        MODE = "piano_roll"

    elif args.kflags["mode"] == "music":
        MODE = "music"


# Configure your modes files
if MODE == "music":

    INPUT_AUDIO = THIS_FILE_DIR + "/assets/free_assets/kawaii_bass.ogg"

    # "image" or "video"
    BACKGROUND_TYPE = "image"  
    # BACKGROUND_TYPE = "video"

    # User defined background or MMV-generated one? "user", "generated"
    # Only applied for BACKGROUND_TYPE = "image"
    BACKGROUND_MODE = "generated"

    # Image background
    if BACKGROUND_TYPE == "image":

        # User set background
        if BACKGROUND_MODE == "user": 
            BACKGROUND_IMAGE = THIS_FILE_DIR + "/assets/some/background.jpg"
            # BACKGROUND_IMAGE = "/home/tremeschin/some/background.jpg"
            # BACKGROUND_IMAGE = "~/some/background.jpg"

        # Generate a neat "procedural" background
        elif BACKGROUND_MODE == "generated":

            # Background we save by default
            GENERATED_BACKGROUND_DIRECTORY = THIS_FILE_DIR + "/assets/generated/background"

            # Delete the directory, reset its file contents
            # Change "if True:" to "if False:" for keeping files, also
            # change the number of generated images to something higher :)
            if True:
                processing.delete_directory(GENERATED_BACKGROUND_DIRECTORY)
                processing.make_directory_if_doesnt_exist(GENERATED_BACKGROUND_DIRECTORY)

            # Initialize a canvas we'll generate the backgrounds
            skia = SkiaNoWindowBackend()
            skia.init(
                width = processing.width,
                height = processing.height,
            )

            # Get a pygradienter object for generating the images
            pygradienter = processing.pygradienter(
                skia = skia,
                width = processing.width,
                height = processing.height,
                n_images = 1,
                output_dir = GENERATED_BACKGROUND_DIRECTORY,
                mode = "polygons"
            )

            # Generate random backgrounds and quit canvas
            pygradienter.run()
            skia.terminate_glfw()
            
            BACKGROUND_IMAGE = processing.random_file_from_dir(GENERATED_BACKGROUND_DIRECTORY)

    # Video background
    elif BACKGROUND_TYPE == "video":
        BACKGROUND_VIDEO = THIS_FILE_DIR + "/assets/video.mp4"  # TODO: NO DEMO VIDEO

    # Logo
    LOGO_IMAGE = THIS_FILE_DIR + "/assets/free_assets/mmv_logo.png"

    # Enable / disable features
    VISUALIZER = True
    LOGO = True

# Piano Roll general configuration
elif MODE == "piano_roll":

    INPUT_MIDI  = THIS_FILE_DIR + "/assets/free_assets/piano_roll/contingency_times.mid"

    # "auto" or "manual"
    #   auto: Downloads and uses musescore for converting midi -> audio
    #   manutal: You configure the final audio of the video

    # AUDIO_OF_MIDI = "auto"
    AUDIO_OF_MIDI = "auto"

    # Invalid setting assertion
    if not AUDIO_OF_MIDI in ["manual", "auto"]:
        raise RuntimeError(f"Invalid option AUDIO_OF_MIDI=[{AUDIO_OF_MIDI}]")

    # Manual config
    if AUDIO_OF_MIDI == "manual":
        INPUT_AUDIO = THIS_FILE_DIR + "/assets/free_assets/piano_roll/contingency_times.ogg"

    # Automatic conversion, NOT IMPLEMENTED FOR WINDOWS
    elif AUDIO_OF_MIDI == "auto":

        # Check and download musescore (Windows only, Linux homies pls install from package manager)
        # or head to [https://musescore.org/en/download]
        interface.download_check_musescore()
        
        # Get a MidiFile class and load the Midi
        midi = processing.get_midi_class()

        # Save the converted audio on the same directory, change .mid to .mp3
        rendered_midi_to_audio_path = INPUT_MIDI.replace(".mid", ".mp3")

        # Remove this file so we render again if you change any setting
        if os.path.exists(rendered_midi_to_audio_path):
            os.remove(rendered_midi_to_audio_path)

        # Convert and assign
        INPUT_AUDIO = midi.convert_to_audio(
            source_path = INPUT_MIDI,
            save_path = rendered_midi_to_audio_path,
            musescore_binary = interface.utils.get_executable_with_name("musescore"),
            bitrate = 400000,
        )
    

    # If your audio is delayed according to the midi, delay the notes by how much seconds?

    # Amount of piano keys content dropping down on screen
    PIANO_ROLL_SECONDS_OF_MIDI_CONTENT_ON_SCREEN = 3

    # # Set BPM of your MIDI file, not stable for me to get for you :(
    
    # Weirdly enough this changes the BPM, I'm not sure..
    # Maybe Ardour didn't set the BPM of the MIDI file to 130?
    # Or did fluidsynth default to 120 BPM and say that was it
    
    if AUDIO_OF_MIDI == "auto":
        PIANO_ROLL_MIDI_BPM = 120

    elif AUDIO_OF_MIDI == "manual":
        PIANO_ROLL_MIDI_BPM = 130


# # Quick enable and disable features used in both music and piano roll mode

# Both
PROGRESSION_BAR = True

# # Depends on mode
if MODE == "piano_roll":
    PROGRESSION_BAR_POSITION = "top"
    PARTICLES = False  # Particles don't go along pretty well with the piano roll (yet?)
    VIGNETTING = False  # I like vignetting on the piano roll but it hurts a bit the visibility
else:
    PROGRESSION_BAR_POSITION = "bottom"
    PARTICLES = True
    VIGNETTING = True


# By default we store the videos in this RENDER_DIR, create it if it doesn't exist
RENDER_DIR = THIS_FILE_DIR + "/renders"
processing.make_directory_if_doesnt_exist(RENDER_DIR)

# Where we'll output the video
# You can set like OUTPUT_VIDEO = "mmv_output.mkv"
# I recommend MKV because if something fails you don't lose the footage,
# the MP4 containers we must finish the pipe process for it to be readable
# Set this to "auto" for automatic file name, as seen on following conditional.
OUTPUT_VIDEO = "auto"

if OUTPUT_VIDEO == "auto":
    now = datetime.datetime.now()
    date_and_time = now.strftime("%Y-%m-%d_%H-%M-%S")  # Don't put ":"" here, Windows doesn't like it, took a while to figure lol
    OUTPUT_VIDEO = (
        RENDER_DIR + "/"
        f"mmv_{date_and_time}_"
        f"mode-{MODE}_"
        f"fps-{processing.mmv_main.context.fps}_"
        f"{os.path.splitext(os.path.basename(INPUT_AUDIO))[0]}"  # Filename of the audio without extension
        ".mkv"
    )


# # Configurations on some modules, presets

"""
PARTICLES_PRESET:
    "middle_out": Particles start from the middle of the screen and diverges from its origin
    "bottom_mid_top": Particles grow from below, stop at middle screen for a moment, runs and fades out upwards
"""
PARTICLES_PRESET = "middle_out"
# PARTICLES_PRESET = "bottom_mid_top"


# You can configure the other stuff as follow, better to look at their
# functions on what they do first


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# I don't share my logo files because that's my identity but the preset I use is kinda here
TREMX_LOGO = False

"""
# # # [ IMPORTANT ] # # #

When setting coordinates like path points, the reference is the following:

Center (0, 0) is at the top left corner of the video,
and the "object" position is at the top left corner of its image as well

X increases rightwards
Y increases downwards
"""


# Generate random particles
if PARTICLES:
    PARTICLES_DIRECTORY = THIS_FILE_DIR + "/assets/generated/particles"
    processing.delete_directory(PARTICLES_DIRECTORY)
    processing.make_directory_if_doesnt_exist(PARTICLES_DIRECTORY)

    # Size of the particle image
    particle_width = 200
    particle_height = 200
    generate_n = 50 # particles

    # Create canvas to draw on
    skia = SkiaNoWindowBackend()
    skia.init(width = particle_width, height = particle_height)

    # Get a pygradienter object with particle mode
    pygradienter = processing.pygradienter(
        skia = skia,
        width = particle_width,
        height = particle_height,
        n_images = generate_n,
        output_dir = PARTICLES_DIRECTORY,
        mode = "particles",
    )

    # Run it
    pygradienter.run()


# The way we process and get the frequencies from the audio, highly
# influences the frequencies bars on the visualizer itself
processing.audio_processing.preset_balanced()

# I/O options, input a audio, output a video
processing.input_audio(INPUT_AUDIO)
processing.output_video(OUTPUT_VIDEO)

if (MODE == "piano_roll"):
    processing.input_midi(INPUT_MIDI)

# # # Background

# Image background
if (MODE == "music") and (BACKGROUND_TYPE == "image"):

    # Get an MMV image object
    background = processing.image_object()

    # We can load an random image from the dir :)
    background.configure.load_image(BACKGROUND_IMAGE)

    # As the background fills the video, we resize it to the video resolution
    # But we'll add a shake modifier to it by that amount of pixels on each direction
    # So we have to over resize a bit the background so the shake doesn't make black borders
    # And start it shake amounts off the screen
    shake = 20
    background.configure.resize_image_to_video_resolution(
        over_resize_width = 2*shake,
        over_resize_height = 2*shake,
    )

    # Set the object fixed point position off screen
    background.configure.add_path_point(x = -shake, y = -shake)

    # Shake by "shake" amount of pixels at max on any direction
    background.configure.simple_add_path_modifier_shake(
        shake_max_distance = shake,
        x_smoothness = 0.01,
        y_smoothness = 0.01,
    )

    # Blur the background when the average audio amplitude increases
    background.configure.add_module_blur(
        smooth = 0.1,
        scalar = 15
    )

    # Resize the background when the average audio amplitude increases
    background.configure.add_module_resize(
        smooth = 0.05,
        scalar = 2,
    )

    # Add the backround object to be generated
    # The layers are a ascending order of blitted items, 0 is first, 1 is after zero
    # So our background is before everything, layer 0
    processing.add(background, layer=0)

# Video background
elif (MODE == "music") and (BACKGROUND_TYPE == "video"):
    # Get an MMV image object
    background = processing.image_object()

    # On videos they are automatically resized to the output
    # resolution and find this shake value automatically
    shake = 15

    # We can load an video :)
    background.configure.add_module_video(
        path = BACKGROUND_VIDEO,
        width = processing.width,
        height = processing.height,
        over_resize_width = 2*shake,
        over_resize_height = 2*shake,
    )

    # Set the object fixed point position off screen
    background.configure.add_path_point(x = 0, y = 0)

    # Shake by "shake" amount of pixels at max on any direction
    background.configure.simple_add_path_modifier_shake(
        shake_max_distance = shake,
        x_smoothness = 0.01,
        y_smoothness = 0.01,
    )

    # Blur the background when the average audio amplitude increases
    background.configure.add_module_blur(
        smooth = 0.2,
        scalar = 16,
    )

    # Resize the background when the average audio amplitude increases
    background.configure.add_module_resize(
        smooth = 0.1,
        scalar = 0.5,
    )

    # Add the backround object to be generated
    # The layers are a ascending order of blitted items, 0 is first, 1 is after zero
    # So our background is before everything, layer 0
    processing.add(background, layer=0)

elif (MODE == "music"):
    exit("No valid background set for MODE=music")

# Piano roll

if (MODE == "piano_roll"):
    piano_roll = processing.image_object()
    piano_roll.configure.add_module_piano_roll(
        seconds_of_midi_content = PIANO_ROLL_SECONDS_OF_MIDI_CONTENT_ON_SCREEN,
        bpm = PIANO_ROLL_MIDI_BPM,
    )
    processing.add(piano_roll, layer=1)

# # # Logo

logo_size = (190/720)*processing.height

# Default MMV Logo
if ((MODE == "music") and LOGO) and (not TREMX_LOGO):
    # Our logo size, it's a good thing to keep it proportional according to the resolution
    # so I set it to a 200/720 proportion on a HD 720p resolution, but I have to multiply by
    # the new resolution afterwards

    logo = processing.image_object()
    logo.configure.load_image(LOGO_IMAGE)
    logo.configure.resize_image_to_resolution(
        width = logo_size,
        height = logo_size,
        override = True
    )

    # The starting point is a bit hard to understand, we want to center it but have to
    # account the logo size, so the first part gets the center point of the resolution
    # and the second part subtracts half the logo size on each Y and X direction
    logo.configure.add_path_point(
        x = (processing.width // 2) - (logo_size/2),
        y = (processing.height // 2) - (logo_size/2),
    )

    logo.configure.add_module_resize(
        smooth = 0.3,
        scalar = 2,
    )

    # We can add rotation to the object
    logo.configure.add_module_swing_rotation(
        max_angle = 6,
        smooth = 100,
    )

    processing.add(logo, layer=4)

# Tremx logo
# You can't run this as I don't include the files, it's here more for you to learn and get
# some ideas on what is possible with MMV
if ((MODE == "music") and LOGO) and (TREMX_LOGO):

    # # # Black disk logo

    black_disk_logo = processing.image_object()
    black_disk_logo.configure.load_image(THIS_FILE_DIR + "/assets/tremx_assets/logo/black-disk.png")
    black_disk_logo.configure.resize_image_to_resolution(
        width = logo_size,
        height = logo_size,
        override = True
    )

    black_disk_logo.configure.add_path_point(
        x = (processing.width // 2) - (logo_size/2),
        y = (processing.height // 2) - (logo_size/2),
    )

    black_disk_logo.configure.add_module_resize(
        smooth = 0.3,
        scalar = 2,
    )

    processing.add(black_disk_logo, layer = 4)

    # # # Sawtooth logo

    sawtooth_logo = processing.image_object()
    sawtooth_logo.configure.load_image(THIS_FILE_DIR + "/assets/tremx_assets/logo/sawtooth.png")
    sawtooth_logo.configure.resize_image_to_resolution(
        width = logo_size,
        height = logo_size,
        override = True
    )

    sawtooth_logo.configure.add_path_point(
        x = (processing.width // 2) - (logo_size/2),
        y = (processing.height // 2) - (logo_size/2),
    )

    sawtooth_logo.configure.add_module_resize(
        smooth = 0.3,
        scalar = 2,
    )

    # We can add rotation to the object
    sawtooth_logo.configure.add_module_swing_rotation(
        max_angle = 4.5,
        smooth = 60,
    )

    processing.add(sawtooth_logo, layer = 5)

    # # # Sine Wave logo

    sawtooth_logo = processing.image_object()
    sawtooth_logo.configure.load_image(THIS_FILE_DIR + "/assets/tremx_assets/logo/sine.png")
    sawtooth_logo.configure.resize_image_to_resolution(
        width = logo_size,
        height = logo_size,
        override = True
    )

    sawtooth_logo.configure.add_path_point(
        x = (processing.width // 2) - (logo_size/2),
        y = (processing.height // 2) - (logo_size/2),
    )

    sawtooth_logo.configure.add_module_resize(
        smooth = 0.3,
        scalar = 2,
    )

    # We can add rotation to the object
    sawtooth_logo.configure.add_module_swing_rotation(
        max_angle = 5,
        smooth = 140,
    )

    processing.add(sawtooth_logo, layer = 5)


# Circle visualizer
if (MODE == "music") and VISUALIZER:
    # Create a visualizer object, see [TODO] wiki for more information
    visualizer = processing.image_object()
    visualizer.configure.add_module_visualizer(
        type = "circle",
        minimum_bar_size = logo_size//2,
        maximum_bar_size = 260,
        bar_responsiveness = 0.6,
        bigger_bars_on_magnitude_add_magnitude_divided_by = 64,
        bar_magnitude_multiplier = 4,
    )

    # visualizer.configure.simple_add_linear_blur(intensity="high")
    visualizer.configure.add_module_resize(
        smooth = 0.12,
        scalar = 2,
    )

    processing.add(visualizer, layer=3)


# # Post processing / effects

# Particle generator
if PARTICLES:
    generator = processing.generator_object()

    # See "./mmv/mmv/generators/mmv_particle_generator.py" for configuration, we use the default one here
    generator.particle_generator(
        preset = PARTICLES_PRESET,
        particles_images_directory = PARTICLES_DIRECTORY,
        particle_minimum_size = 0.04,
        particle_maximum_size = 0.085,
    )

    processing.add(generator)

# Bottom progression bar
if PROGRESSION_BAR:
    # Add basic progression bar
    prog_bar = processing.image_object()

    if MODE == "music":
        shake_scalar = 14
    elif MODE == "piano_roll":
        shake_scalar = 0
        
    prog_bar.configure.add_module_progression_bar(
        bar_type = "rectangle",
        bar_mode = "simple",
        position = PROGRESSION_BAR_POSITION,
        shake_scalar = shake_scalar,
    )

    processing.add(prog_bar, layer=4)


if VIGNETTING:
    # Add simple vignetting on default configs on the post processing
    # Those darken the edges of the screen when the average amplitude of the audio
    # goes up, mostly with the bass. Search for vignetting, you'll see what I mean
    processing.post_processing.add_module_vignetting(
        start = processing.width*1.3,
        minimum = 800,
        scalar = - 1000,
        smooth = 0.1,
    )


# Run and generate the final video
processing.run()
