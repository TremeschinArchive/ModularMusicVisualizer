"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
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

from modules.end_user_utilities import ArgParser
import sys

# Parse shell arguments
args = ArgParser(sys.argv)

# # # MMV

# Import MMV module
import mmv

# Import a "canvas" class for generating background image video textures
from mmv.mmvskia.pyskt.pyskt_backend import SkiaNoWindowBackend

# For auto naming files according to when you run MMV
import datetime

# For us to refer relative paths to this base_video.py
# THIS_FILE_DIR = path directory of where this file is located without the last "/"
# It is assumed this file is under /repository_folder/src/base_video.py so 
# THIS_FILE_DIR is "/repository_folder/mmv"
import os
THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the wrapper class
interface = mmv.MMVPackageInterface()

# # Get MMVSkia interface
mmv_skia_interface = interface.get_skia_interface()

# Configure stuff
mmv_skia_interface.configure_mmv_skia_main(

    # # MMV settings

    # If your audio isn't properly normalized or you want a more aggressive video,
    # set this to 1.5 - 2 or so.
    audio_amplitude_multiplier = 1.1,

    # Use or not a GPU accelerated context, pass render=gpu or render=cpu flags
    # For higher resolutions 720p+, GPUs are definitely faster for raw output
    # but for smaller res, CPUs win on image transfering, it defaults to GPU
    # on the final video render if no flag was passed. Generating images such as
    # particles and backgrounds is done on CPU as no textures are being moved.
    render_backend = args.render,

    # You can pass the argument "preview" when executing this file otherwise set it manually here
    # Preview have little to no performance impact and render to video slow down stuff quite a bit
    show_preview_window = "preview" in args.flags,
    render_to_video = not "preview" in args.flags,
    # show_preview_window = True,
    # render_to_video = True,
)


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
mmv_skia_interface.quality(
    
    # # # [ Common resolution values ] # # #

    # # ["4k" / 2160p]
    # width = 3840,
    # height = 2160,

    # # [Quad HD 1440p]
    # width = 2560,
    # height = 1440,

    # # [WFHD Ultra Wide Full HD 1080p]
    # width = 2560,
    # height = 1080,

    # [Full HD 1080p]
    width = 1920,
    height = 1080,

    # # [HD SD 720p]
    # width = 1280,
    # height = 720,

    # # [SD 480p]
    # width = 854,
    # height = 480,

    # # # [ Common FPS values ] # # #

    # fps = 240,
    # fps = 144,
    fps = 60,
    # fps = 30,
    # fps = 24,
)

mmv_skia_interface.fft(
    # # # [ FFT config ] # # #
    batch_size = 4096,
)

# Ensure we have FFmpeg on Windows, downloads, extracts etc
# Does nothing for Linux, make sure you have ffmpeg package installed on your distro
interface.check_download_externals(target_externals = ["ffmpeg"])

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def generate_some_background_image():

    # Background we save by default
    GENERATED_BACKGROUND_DIRECTORY = THIS_FILE_DIR + "/assets/generated/background"

    # Reset from previous ones
    mmv_skia_interface.delete_directory(GENERATED_BACKGROUND_DIRECTORY)
    mmv_skia_interface.make_directory_if_doesnt_exist(GENERATED_BACKGROUND_DIRECTORY)

    # Initialize a canvas we'll generate the backgrounds
    skia = SkiaNoWindowBackend()
    skia.init(
        width = mmv_skia_interface.width,
        height = mmv_skia_interface.height,
    )

    # Get a pygradienter object for generating the images
    pygradienter = mmv_skia_interface.pygradienter(
        skia = skia,
        width = mmv_skia_interface.width,
        height = mmv_skia_interface.height,
        n_images = 1,
        output_dir = GENERATED_BACKGROUND_DIRECTORY,
        mode = "polygons"
    )

    # Generate random backgrounds and quit canvas
    pygradienter.run()
    skia.terminate_glfw()
    
    return mmv_skia_interface.random_file_from_dir(GENERATED_BACKGROUND_DIRECTORY)
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# We have two main modes "music" and "piano", you can uncomment them

# Default mode
MODE = "music"

# Pass a flag mode=music or mode=piano when calling this script
# if that flag exists, then it overrides that previous MODE
if "mode" in args.kflags:
    MODE = args.kflags["mode"]

# Configure your modes files
if MODE == "music":

    INPUT_AUDIO = THIS_FILE_DIR + "/assets/free_assets/kawaii_bass.ogg"

    # "image" or "video"
    BACKGROUND_TYPE = "image"  
    # BACKGROUND_TYPE = "video"

    # User defined background or MMV-generated one? "user", "generated"
    # Only applied for BACKGROUND_TYPE = "image"
    BACKGROUND_MODE = "generated"
    # BACKGROUND_MODE = "user"

    # Image background
    if BACKGROUND_TYPE == "image":

        # User set background
        if BACKGROUND_MODE == "user": 
            BACKGROUND_IMAGE = THIS_FILE_DIR + "/assets/some/background.jpg"
            # BACKGROUND_IMAGE = "/home/tremeschin/some/background.jpg"
            # BACKGROUND_IMAGE = "~/some/background.jpg"

        # Generate a neat "procedural" background
        elif BACKGROUND_MODE == "generated":
            BACKGROUND_IMAGE = generate_some_background_image()

    # Video background
    elif BACKGROUND_TYPE == "video":
        BACKGROUND_VIDEO = THIS_FILE_DIR + "/assets/video.mp4"  # TODO: NO DEMO VIDEO

    # Logo
    LOGO_IMAGE = THIS_FILE_DIR + "/assets/free_assets/mmv_logo.png"

    # Enable / disable features
    VISUALIZER = True
    LOGO = True

    # Color presets
    VISUALIZER_BARS_COLOR_PRESET = "colorful"  # Available: ["colorful", "white"]

# Piano Roll general configuration
elif MODE == "piano":

    INPUT_MIDI  = THIS_FILE_DIR + "/assets/free_assets/piano_roll/contingency_times.mid"

    # "auto" or "manual"
    #   auto: Downloads and uses musescore for converting midi -> audio
    #   manutal: You configure the final audio of the video

    # AUDIO_OF_MIDI = "auto"
    AUDIO_OF_MIDI = "manual"

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
        interface.check_download_externals(target_externals = ["musescore"])
        
        # Get a MidiFile class and load the Midi
        midi = mmv_skia_interface.get_midi_class()

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
    
    # # Colors and presets

    from modules.piano_roll_colors_helper import PianoRollColorsHelper
    PIANO_ROLL_COLOR = PianoRollColorsHelper()

    # # The background behind the keys
    PIANO_ROLL_BACKGROUND_TYPE = "image"
    # PIANO_ROLL_BACKGROUND_TYPE = "color"

    # Image
    if PIANO_ROLL_BACKGROUND_TYPE == "image":
        
        # Transparent so the image appears
        PIANO_ROLL_COLOR.background("transparent")

        # Get some background image, NOTE: there is no guarantee the colors won't visually
        # overlap with the notes, try your luck here..
        BACKGROUND_IMAGE = generate_some_background_image()

        # Get an MMV image object
        background = mmv_skia_interface.image_object()

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
        background.configure.simple_add_path_modifier_shake(shake_max_distance = shake, x_smoothness = 0.01, y_smoothness = 0.01)

        # Resize the background when the average audio amplitude increases
        background.configure.add_module_resize(smooth = 0.05, scalar = 1.02)

        # Add the backround object to be generated
        # The layers are a ascending order of blited items, 0 is first, 1 is after zero
        # So our background is before everything, layer 0
        mmv_skia_interface.add(background, layer = 0)

    # NOTE: see /src/modules/piano_roll_colors_helper.py for presets and arguments

    # Colors
    elif PIANO_ROLL_BACKGROUND_TYPE == "color":
        PIANO_ROLL_COLOR.background("default")

    # Presets
    PIANO_ROLL_COLOR.piano("default")
    PIANO_ROLL_COLOR.markers("easy")  # default, easy

    PIANO_ROLL_COLOR.set_note_preset(channel = 0, preset = "acid-yellow")
    PIANO_ROLL_COLOR.set_note_preset(channel = 1, preset = "magic-purple")
    PIANO_ROLL_COLOR.set_note_preset(channel = 2, preset = "forest-green")
    PIANO_ROLL_COLOR.set_note_preset(channel = 3, preset = "vibrant-red")

    # Rounded corners of the notes and keys
    PIANO_ROLL_ROUNDING = {
        "piano_keys": {
            "white": {"x": 8, "y": 4},
            "black": {"x": 8, "y": 4}
        },
        "notes": {"x": 4, "y": 4}
    }

    # This will ignore the pressing colors states of the color dictionary configuration, setting
    # this to True will get a color similar to the note being played (the white key non sharp ones)
    PIANO_ROLL_KEY_FOLLOWS_NOTE_COLOR = True

    # Draw the note name (C, D, G, A#..)
    PIANO_ROLL_DRAW_NOTE_NAME = True

    # The amount of extra keys we render on each side past the maximum and minimum ones played
    # Higher value means "bigger" piano and more center-focused content, less values yields easier to
    # visualize piano for beginners and looks kinda more childish.
    # Recommended minimum is 3 and a value of 10 should be ok for everything.
    # The piano scales infinitely so put 50, 100, 300 at your own will just for fun..
    PIANO_ROLL_AMOUNT_BLEED = 10

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
if MODE == "piano":
    PROGRESSION_BAR_POSITION = "top"
    PARTICLES = False  # Particles don't go along pretty well with the piano roll (yet?)
    VIGNETTING = False  # I like vignetting on the piano roll but it hurts a bit the visibility
else:
    PROGRESSION_BAR_POSITION = "bottom"
    PARTICLES = True
    VIGNETTING = True

"""
PARTICLES_PRESET:
    "middle_out": Particles start from the middle of the screen and diverges from its origin
    "bottom_mid_top": Particles grow from below, stop at middle screen for a moment, runs and fades out upwards
"""
PARTICLES_PRESET = "middle_out"
# PARTICLES_PRESET = "bottom_mid_top"

# # Configurations on some modules, presets

if mmv_skia_interface.mmv_skia_main.context.render_to_video:

    # By default we store the videos in this RENDER_DIR, create it if it doesn't exist
    RENDER_DIR = THIS_FILE_DIR + "/renders"
    mmv_skia_interface.make_directory_if_doesnt_exist(RENDER_DIR)

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
            f"fps-{mmv_skia_interface.mmv_skia_main.context.fps}_"
            f"{os.path.splitext(os.path.basename(INPUT_AUDIO))[0]}"  # Filename of the audio without extension
            ".mkv"
        )

    # # Video encoding

    video_encoder = interface.get_ffmpeg_wrapper()
    video_encoder.configure_encoding(
        ffmpeg_binary_path = interface.find_binary("ffmpeg"),
        width = mmv_skia_interface.width,
        height = mmv_skia_interface.height,
        input_audio_source = INPUT_AUDIO,
        input_video_source = "pipe",
        output_video = OUTPUT_VIDEO,
        pix_fmt = "rgba",  # If you get swapped red and blue color channels try setting this to bgra
        framerate = mmv_skia_interface.fps,

        # Encoder preset, possible values are:
        #  > ["placebo", "veryslow", "slowest", "slow",
        #     "medium", "fast", "faster", "veryfast",
        #     "superfast", "ultrafast"]
        #
        # Slower presets yields a higher quality encoding but utilize more CPU,
        # since MMVSkia is by no means no realtime, a slow preset should be enough since
        # the FFmpeg process is run in parallel. 
        preset = "slow",

        # Try utilizing hardware acceleration? Set to None for ignoring this
        hwaccel = "auto",

        # Don't overflow the subprocess buffer
        loglevel = "panic",
        nostats = True,
        hide_banner = True,

        # If True adds "-x264opts opencl" to the FFmpeg command. Can make FFmpeg have a
        # startup time of a few seconds, will disable for compatibility since not everyone
        # have opencl loaders, etc.
        opencl = False,

        # Constant Rate Factor of x264 or x265 encoding, 0 is lossless, 51 is the worst,
        # 23 the the default. Low values means higher quality and bigger file size
        crf = 17,

        # Tune video encoder for:
        # "film":       Mostly IRL stuff, shouldn't hurt letting this default
        # "animation":  Animes in general, we use this default as
        # "grain":      Optimized for old / grainy contents for preserving it
        # "fastdecode": For low compute power devices to have less trouble with
        tune = "film",

        vflip = False,
        vcodec = "libx264",
        override = True,
    )

    # Set the encoder
    mmv_skia_interface.pipe_video_to(
        pipe_video_to = video_encoder    
    )

    mmv_skia_interface.output_video(OUTPUT_VIDEO)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

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

# # # # # # Advanced

# mmv_skia_interface.advanced_audio_mmv_skia_interface_constants(
#     where_decay_less_than_one = 440,
#     value_at_zero = 5
# )

# # # # # # # # # #

# Generate random particles
if PARTICLES:
    PARTICLES_DIRECTORY = THIS_FILE_DIR + "/assets/generated/particles"
    mmv_skia_interface.delete_directory(PARTICLES_DIRECTORY)
    mmv_skia_interface.make_directory_if_doesnt_exist(PARTICLES_DIRECTORY)

    # Size of the particle image
    particle_width = 200
    particle_height = 200
    generate_n = 50 # particles

    # Create canvas to draw on
    skia = SkiaNoWindowBackend()
    skia.init(width = particle_width, height = particle_height)

    # Get a pygradienter object with particle mode
    pygradienter = mmv_skia_interface.pygradienter(
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
mmv_skia_interface.audio_processing.preset_balanced()

# I/O options, input a audio, output a video
mmv_skia_interface.input_audio(INPUT_AUDIO)

if (MODE == "piano"):
    mmv_skia_interface.input_midi(INPUT_MIDI)

# # # Background

# Image background
if (MODE == "music") and (BACKGROUND_TYPE == "image"):

    # Get an MMV image object
    background = mmv_skia_interface.image_object()

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
    # The layers are a ascending order of blited items, 0 is first, 1 is after zero
    # So our background is before everything, layer 0
    mmv_skia_interface.add(background, layer=0)

# Video background
elif (MODE == "music") and (BACKGROUND_TYPE == "video"):
    # Get an MMV image object
    background = mmv_skia_interface.image_object()

    # On videos they are automatically resized to the output
    # resolution and find this shake value automatically
    shake = 15

    # We can load an video :)
    background.configure.add_module_video(
        path = BACKGROUND_VIDEO,
        width = mmv_skia_interface.width,
        height = mmv_skia_interface.height,
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
    mmv_skia_interface.add(background, layer=0)

elif (MODE == "music"):
    exit("No valid background set for MODE=music")

# Piano roll

if (MODE == "piano"):

    piano_roll = mmv_skia_interface.image_object()
    piano_roll.configure.add_module_piano_roll(
        seconds_of_midi_content = PIANO_ROLL_SECONDS_OF_MIDI_CONTENT_ON_SCREEN,
        bpm = PIANO_ROLL_MIDI_BPM,
        colors = PIANO_ROLL_COLOR.colors,
        piano_key_follows_note_color = PIANO_ROLL_KEY_FOLLOWS_NOTE_COLOR,
        rounding = PIANO_ROLL_ROUNDING,
        draw_note_name = PIANO_ROLL_DRAW_NOTE_NAME,
        bleed = PIANO_ROLL_AMOUNT_BLEED,
    )
    mmv_skia_interface.add(piano_roll, layer = 3)

# # # Logo

logo_size = (190/720)*mmv_skia_interface.height

# Default MMV Logo
if ((MODE == "music") and LOGO) and (not TREMX_LOGO):
    # Our logo size, it's a good thing to keep it proportional according to the resolution
    # so I set it to a 200/720 proportion on a HD 720p resolution, but I have to multiply by
    # the new resolution afterwards

    logo = mmv_skia_interface.image_object()
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
        x = (mmv_skia_interface.width // 2) - (logo_size/2),
        y = (mmv_skia_interface.height // 2) - (logo_size/2),
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

    mmv_skia_interface.add(logo, layer=4)

# Tremx logo
# You can't run this as I don't include the files, it's here more for you to learn and get
# some ideas on what is possible with MMV
if ((MODE == "music") and LOGO) and (TREMX_LOGO):

    # # # Black disk logo

    black_disk_logo = mmv_skia_interface.image_object()
    black_disk_logo.configure.load_image(THIS_FILE_DIR + "/assets/tremx_assets/logo/black-disk.png")
    black_disk_logo.configure.resize_image_to_resolution(
        width = logo_size,
        height = logo_size,
        override = True
    )

    black_disk_logo.configure.add_path_point(
        x = (mmv_skia_interface.width // 2) - (logo_size/2),
        y = (mmv_skia_interface.height // 2) - (logo_size/2),
    )

    black_disk_logo.configure.add_module_resize(
        smooth = 0.3,
        scalar = 2,
    )

    mmv_skia_interface.add(black_disk_logo, layer = 4)

    # # # Sawtooth logo

    sawtooth_logo = mmv_skia_interface.image_object()
    sawtooth_logo.configure.load_image(THIS_FILE_DIR + "/assets/tremx_assets/logo/sawtooth.png")
    sawtooth_logo.configure.resize_image_to_resolution(
        width = logo_size,
        height = logo_size,
        override = True
    )

    sawtooth_logo.configure.add_path_point(
        x = (mmv_skia_interface.width // 2) - (logo_size/2),
        y = (mmv_skia_interface.height // 2) - (logo_size/2),
    )

    sawtooth_logo.configure.add_module_resize(
        smooth = 0.7,
        scalar = 2,
    )

    # We can add rotation to the object
    sawtooth_logo.configure.add_module_swing_rotation(
        max_angle = 4.5,
        smooth = 60,
    )

    mmv_skia_interface.add(sawtooth_logo, layer = 5)

    # # # Sine Wave logo

    sawtooth_logo = mmv_skia_interface.image_object()
    sawtooth_logo.configure.load_image(THIS_FILE_DIR + "/assets/tremx_assets/logo/sine.png")
    sawtooth_logo.configure.resize_image_to_resolution(
        width = logo_size,
        height = logo_size,
        override = True
    )

    sawtooth_logo.configure.add_path_point(
        x = (mmv_skia_interface.width // 2) - (logo_size/2),
        y = (mmv_skia_interface.height // 2) - (logo_size/2),
    )

    sawtooth_logo.configure.add_module_resize(
        smooth = 0.6,
        scalar = 2,
    )

    # We can add rotation to the object
    sawtooth_logo.configure.add_module_swing_rotation(
        max_angle = 5,
        smooth = 140,
    )

    mmv_skia_interface.add(sawtooth_logo, layer = 5)


# Circle visualizer
if (MODE == "music") and VISUALIZER:
    # Create a visualizer object, see [TODO] wiki for more information
    visualizer = mmv_skia_interface.image_object()
    visualizer.configure.add_module_visualizer(
        type = "circle",
        minimum_bar_size = logo_size//2,
        maximum_bar_size = 300,
        bar_responsiveness = 0.6,
        bigger_bars_on_magnitude_add_magnitude_divided_by = 32,
        bar_magnitude_multiplier = 4,
        color_preset = VISUALIZER_BARS_COLOR_PRESET,

        # Advanced config (sorta)
        fft_20hz_multiplier = 0.8,
        fft_20khz_multiplier = 12,
    )

    # visualizer.configure.simple_add_linear_blur(intensity="high")
    visualizer.configure.add_module_resize(
        smooth = 0.12,
        scalar = 2.1,
    )

    mmv_skia_interface.add(visualizer, layer=3)


# # Post mmv_skia_interface / effects

# Particle generator
if PARTICLES:
    generator = mmv_skia_interface.generator_object()

    # See "./mmv/mmv/generators/mmv_skia_particle_generator.py" for configuration, we use the default one here
    generator.particle_generator(
        preset = PARTICLES_PRESET,
        particles_images_directory = PARTICLES_DIRECTORY,
        particle_minimum_size = 0.04,
        particle_maximum_size = 0.085,
    )

    mmv_skia_interface.add(generator)

# Bottom progression bar
if PROGRESSION_BAR:
    # Add basic progression bar
    prog_bar = mmv_skia_interface.image_object()

    if MODE == "music":
        shake_scalar = 14
    elif MODE == "piano":
        shake_scalar = 0
        
    prog_bar.configure.add_module_progression_bar(
        bar_type = "rectangle",
        bar_mode = "simple",
        position = PROGRESSION_BAR_POSITION,
        shake_scalar = shake_scalar,
    )

    mmv_skia_interface.add(prog_bar, layer=4)


if VIGNETTING:
    # Add simple vignetting on default configs on the post mmv_skia_interface
    # Those darken the edges of the screen when the average amplitude of the audio
    # goes up, mostly with the bass. Search for vignetting, you'll see what I mean
    mmv_skia_interface.post_processing.add_module_vignetting(
        start = mmv_skia_interface.width*1.3,
        minimum = 800,
        scalar = - 1000,
        smooth = 0.1,
    )


# Run and generate the final video
mmv_skia_interface.run()
