"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Test unit for the upcoming MMVShaderMGL
This is a temporary file, proper interface for MGLShader is planned

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

debug_prefix = "[run_shaders.py]"
from tqdm import tqdm
from PIL import Image
import numpy as np
import threading
import random
import shutil
import time
import math
import sys
import os


class ArgParser:
    def __init__(self, argv):
        # Empty list of flags and kflags
        self.flags = []
        self.kflags = {}

        if argv is not None:

            # Iterate in all args
            for arg in argv[1:]:
                
                # Is a kwarg
                if "=" in arg:
                    arg = arg.split("=")
                    self.kflags[arg[0]] = arg[1]

                # Is a flag
                else:
                    self.flags.append(arg)

# Parse shell arguments TODO: proper interface using typer?
# Temporary file mostly?
args = ArgParser(sys.argv)

# List and override soundcard outputs
if ("list" in args.flags):
    import soundcard
    print(f"{debug_prefix} Available devices to record audio:")
    for index, device in enumerate(soundcard.all_microphones(include_loopback = True)):
        print(f"{debug_prefix} > ({index}) [{device.name}]")
    print(f"{debug_prefix} :: Run this script again with [capture=N] flag to override")
    sys.exit(0)

# Overriding capture stuff
cap = args.kflags.get("capture", None)
override_record_device = None

if cap is not None:
    import soundcard
    recordable = soundcard.all_microphones(include_loopback = True)

    # Erro assertion
    if (len(recordable) < int(cap)) or (int(cap) < 0):
        raise RuntimeError(f"Target capture device is out of bounds [{cap}] out of (0, {len(recordable)})")

    # Get the device
    for index, device in enumerate(recordable):
        if index == int(cap):
            override_record_device = device
            break

# Append previous folder to path, debug prefix
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)

# Import mmv, get interface
import mmv
interface = mmv.MMVPackageInterface()
shader_interface = interface.get_shader_interface()
mgl = shader_interface.get_mgl_interface(master_shader = True)

# # Externals

# Video encoder (will only auto download for Windows)
interface.check_download_externals(target_externals = ["ffmpeg"])

# # Configuration

# Resolution, fps, real time or audio file sample rate
WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60
YOUR_COMPUTER_AUDIO_SAMPLERATE = 48000

# Multi sampling, leave as 8?
MSAA = 8

# # Music bars

# Calculate the Fourier Transform?
CALCULATE_FFT = True

# More batch size yields more detailed frequency but less responsiveness,
# also it's more expensive to compute, 2048*4 works ok for most, try reducing
# this to 2048 * 2 or just 2048 if you have a weaker CPU
BATCH_SIZE = 2048 * 4

# # Directories
sep = os.path.sep
GLSL_DIR = f"{interface.data_dir}{sep}glsl"
GLSL_INCLUDE_FOLDER = f"{GLSL_DIR}{sep}include"
ASSETS_DIR = f"{interface.assets_dir}{sep}"

# Input audio source
RENDER_MODE_AUDIO_FILE = f"{ASSETS_DIR}{sep}free_assets{sep}kawaii_bass.ogg"

# There are variables called "multiplier" on each mode, change those to get more
# aggressive or smoother animations

# # Render to video or view real time?
# mode = "render"
mode = "view"

if "render" in sys.argv:
    mode = "render"

# # Render mode

# How many loops to render the audio
NLOOPS = 1

# # Micro management

# Set up target render configuration
mgl.target_render_settings(
    width = WIDTH,
    height = HEIGHT,
    fps = FRAMERATE,
)

# Add directories for including #pragma include
mgl.include_dir(GLSL_INCLUDE_FOLDER)

# Which test to run?
test_number = 5
tests = {
    1: {"frag": f"{GLSL_DIR}{sep}test{sep}test_1_simple_shader.glsl"},
    2: {"frag": f"{GLSL_DIR}{sep}test{sep}___test_2_post_fx_png.glsl"},
    3: {"frag": f"{GLSL_DIR}{sep}test{sep}test_3_rt_audio.glsl"},
    4: {"frag": f"{GLSL_DIR}{sep}test{sep}test_4_fourier.glsl"},
    5: {
        "frag": f"{GLSL_DIR}{sep}test{sep}music_bars_master_shader.glsl",
        "replaces": {
            "BACKGROUND_SHADER": f"{GLSL_DIR}{sep}test{sep}music_bars_background.glsl",
            "MUSIC_BARS_SHADER": f"{GLSL_DIR}{sep}test{sep}music_bars_radial.glsl",
            "MUSIC_BARS_SHADER_PFX": f"{GLSL_DIR}{sep}test{sep}music_bars_radial_pfx.glsl",
            "PARTICLES_SHADER": f"{GLSL_DIR}{sep}test{sep}music_bars_particle.glsl",
            "BACKGROUND_IMAGE": f"{ASSETS_DIR}{sep}free_assets{sep}glsl_default_background.jpg",
            # "LOGO": f"{ASSETS_DIR}{sep}free_assets{sep}mmv_logo.png",
            "LOGO_IMAGE": f"{THIS_DIR}{sep}..{sep}repo{sep}mmv_logo_alt_white.png",
        }
    }
}


# Mode is to render, start the video encoder (FFmpeg) and headless window
if mode == "render":

    # Set mgl window mode
    mgl.mode(
        window_class = "headless",
        strict = True,
        vsync = False,
        msaa = MSAA,
    )

    # # Audio source File
    source = interface.get_audio_source_file()

    # Configure with stuff
    source.configure(
        batch_size = BATCH_SIZE,
        sample_rate = None,  # We'll figure out the sample rate in a few, it'll be read on source.init
        target_fps = FRAMERATE,
        do_calculate_fft = CALCULATE_FFT,
    )

    # Read source audio file
    source.init(path = RENDER_MODE_AUDIO_FILE)

    # Micro
    DURATION = source.duration
    SAMPLERATE = source.sample_rate
 
    # # Video Encoder

    video_pipe = interface.get_ffmpeg_wrapper()

    # Settings, see /src/mmv/common/wrappers/wrap_ffmpeg.py for what those do
    video_pipe.configure_encoding(
        ffmpeg_binary_path = interface.find_binary("ffmpeg"),
        width = WIDTH,
        height = HEIGHT,
        input_audio_source = RENDER_MODE_AUDIO_FILE,
        input_video_source = "pipe",
        output_video = "rendered_shader.mkv",
        pix_fmt = "rgb24",
        framerate = FRAMERATE,
        preset = "slow",
        hwaccel = "auto",
        loglevel = "panic",
        nostats = True,
        hide_banner = True,
        opencl = False,
        crf = 23,
        tune = "film",
        vflip = True,
        vcodec = "libx264",
        override = True,
    )
    video_pipe.start()

    # Start the thread to write the images
    threading.Thread(target = video_pipe.pipe_writer_loop, args = (
        DURATION,  # Duration
        FRAMERATE,  # Fps
        DURATION * FRAMERATE,  # Frame count
        50,  # Max images on buffer to be piped
        False,  # Show stats
    ), daemon = True).start()

    # Increase this value to get more aggressiveness or just turn up the computer volume
    multiplier = args.kflags.get("multiplier", None)
    if multiplier is None:
        multiplier = 90
    else:
        multiplier = int(multiplier)

    TOTAL_STEPS = source.steps_per_loop * NLOOPS
    
    # Progress bar
    progress_bar = tqdm(
        total = TOTAL_STEPS,
        mininterval = 1/20,
        unit = " frames",
        dynamic_ncols = True,
        colour = '#38bed6',
        position = 0,
        smoothing = 0.3
    )
    RENDERING_MESSAGE = f"Rendering [{source.duration:.2f}s]({WIDTH}x{HEIGHT}:{FRAMERATE}) MMV video"
    progress_bar.set_description(RENDERING_MESSAGE)
    source.tqdm_bar_message_max_length = len(RENDERING_MESSAGE)

# Mode is to view real time
elif mode == "view":
    SAMPLERATE = YOUR_COMPUTER_AUDIO_SAMPLERATE

    # Start mgl window
    mgl.mode(
        window_class = "glfw",
        vsync = False,
        msaa = MSAA,
        # icon = f"{ASSETS_DIR}{sep}mmv_logo.ico",
        strict = False,
    )

    # # Realtime Audio

    # Search for loopback, configure
    source = interface.get_audio_source_realtime()

    # Configure with stuff
    source.configure(
        batch_size = BATCH_SIZE,
        sample_rate = SAMPLERATE,
        recorder_numframes =  None,
        do_calculate_fft = CALCULATE_FFT
    )

    # Search for a loopback device to get audio from
    # TODO: Proper CLI for better UX
    if (override_record_device is None):
        source.init(search_for_loopback = True)
    else:
        source.init(recorder_device = override_record_device)

    # source.capture_and_process_loop()
    source.start_async()

    # Increase this value to get more aggressiveness or just turn up the computer volume
    multiplier = args.kflags.get("multiplier", None)
    if multiplier is None:
        multiplier = 140
    else:
        multiplier = int(multiplier)

# # Audio Processing

source.audio_processing.configure(config = [
    {
        "original_sample_rate": 48000,
        "target_sample_rate": 1000,
        "start_freq": 60,
        "end_freq": 500,
    },
    {
        "original_sample_rate": 48000,
        "target_sample_rate": 48000,
        "start_freq": 500,
        "end_freq": 20000,
    }
])

MMV_FFTSIZE = source.audio_processing.FFT_length
print(f"{debug_prefix} FFT Size on AudioProcessing is [{MMV_FFTSIZE}]")

# # Load, bootstrap

# Load the shader from the path
cfg = tests[test_number]
sep = os.path.sep

# Default stuff we replace
default_replaces = {
    "MMV_FFTSIZE": MMV_FFTSIZE,
    "WIDTH": WIDTH,
    "HEIGHT": HEIGHT
}

# Merge the two dicts
replaces = default_replaces
if "replaces" in cfg.keys():
    for key in cfg["replaces"].keys():
        replaces[key] = cfg["replaces"][key]

print(f"{debug_prefix} Replaces dictionary: {replaces}")

# Load the shader
mgl.load_shader_from_path(
    fragment_shader_path = cfg["frag"],
    replaces = replaces,
    save_shaders_path = interface.runtime_dir
)

# # FPS calculation bootstrap
start = time.time()
fps_last_n = 120
times = [time.time() + i/FRAMERATE for i in range(fps_last_n)]

# # Temporary pipeline calculations TODO: proper class

smooth_audio_amplitude = 0
smooth_audio_amplitude2 = 0
progressive_amplitude = 0
prevfft = np.array([0.0 for _ in range(MMV_FFTSIZE)], dtype = np.float32)
target_fft = np.array([0.0 for _ in range(MMV_FFTSIZE)], dtype = np.float32)
step = 0

# Pretty print separator
s = "-"*shutil.get_terminal_size()[0]; print(f"\n{s}\n")

# # Stuff

# If fps is different than the standard 60, we have to recalculate our ratios of interpolation
# between frame (N - 1) and (N), which are the remaining distance times a ratio
def ratio_on_other_fps_based_on_fps(ratio, new_fps, old_fps = 60):
    return 1.0 - ((1.0 - ratio)**(old_fps / new_fps))

try:
    source.start()

    # Main test routine
    while True:

        # The time this loop is starting
        startcycle = time.time()

        # Calculate the fps
        fps = round(fps_last_n / (max(times) - min(times)), 1)
        
        # Info we pass to the shader, this is WIP and hacky rn
        pipeline_info = {}

        # Next iteraion of some audio reader
        source.next(step)

        # We have:
        # - average_amplitudes: vec3 array, L, R and Mono
        pipeline_info = source.get_info()

        # # Temporary stuff

        # Amplitudes
        if "average_amplitudes" in pipeline_info.keys():
            ratio = ratio_on_other_fps_based_on_fps(0.054, FRAMERATE)
            smooth_audio_amplitude = smooth_audio_amplitude + (pipeline_info["average_amplitudes"][2] - smooth_audio_amplitude) * ratio
            pipeline_info["smooth_audio_amplitude"] = smooth_audio_amplitude * multiplier 

            ratio = ratio_on_other_fps_based_on_fps(0.08, FRAMERATE)
            smooth_audio_amplitude2 = smooth_audio_amplitude2 + (pipeline_info["average_amplitudes"][2] - smooth_audio_amplitude2) * ratio
            pipeline_info["smooth_audio_amplitude2"] = smooth_audio_amplitude2 * multiplier * 1.5

            progressive_amplitude += pipeline_info["average_amplitudes"][2]
            pipeline_info["progressive_amplitude"] = progressive_amplitude

        # If we have an fft key, set to the target and delete the one on the pipeline
        # This is to avoid some possible race condition
        if "fft" in pipeline_info.keys():
            target_fft = pipeline_info["fft"]
            del pipeline_info["fft"]

        # More temporary interpolation
        for index, value in enumerate(target_fft):
            ratio = ratio_on_other_fps_based_on_fps(0.25, FRAMERATE)
            prevfft[index] = prevfft[index] + (value*multiplier - prevfft[index]) * ratio

        # Write the FFT
        mgl.write_texture_pipeline(texture_name = "fft", data = prevfft.astype(np.float32))

        # DEBUG: print pipeline
        # print(pipeline_info)

        # Next iteration
        mgl.next(custom_pipeline = pipeline_info)

        # If we'll be rendering, write to the video encoder
        if mode == "render":
            progress_bar.update(1)
            mgl.read_into_subprocess_stdin(video_pipe.subprocess.stdin)
            # video_pipe.write_to_pipe(step, mgl.read())

            # Looped the audio one time, exit
            if step == TOTAL_STEPS:
                video_pipe.subprocess.stdin.close()
                break

        elif mode == "view":
            mgl.update_window()

            # The window received close command
            if mgl.window_should_close:
                break

        # Print FPS, well, kinda, the average of the last fps_last_n frames
        times[step % fps_last_n] = time.time()
        # print(f":: Average FPS last ({fps_last_n} frames): [{fps}] \r", end = "", flush = True)
        step += 1

        # Vsync (yea we really need this)
        if (not mgl.vsync) and (not mode == "render"):
            while time.time() - startcycle < 1 / FRAMERATE:
                time.sleep(1 / (FRAMERATE * 100))

    
except KeyboardInterrupt:
    pass

# Stop stuff
if mode == "view":
    source.stop()
if mode == "render":
    progress_bar.close()

sys.exit(0)
exit()

# # Save first frame from the shader and quit

# if False:
#     img = Image.frombytes('RGB', mgl.window.fbo.size, mgl.read())
#     img.save('output.jpg')
#     exit()