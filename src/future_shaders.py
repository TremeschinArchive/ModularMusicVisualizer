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

from PIL import Image
import numpy as np
import threading
import random
import time
import math
import sys
import os

# Append previous folder to path, debug prefix
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
debug_prefix = "[test_mgl.py]"
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)


# Import mmv, get interface
import mmv
interface = mmv.MMVPackageInterface()
shader_interface = interface.get_shader_interface()
mgl = shader_interface.get_mgl_interface(master_shader = True)

# # Configuration

# Resolution, fps, real time or audio file sample rate
WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60
SAMPLERATE = 48000

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
        "frag": f"{GLSL_DIR}{sep}test{sep}test_5_circle_fourier_bg_main.glsl",
        "replaces": {
            "LAYER1": f"{GLSL_DIR}{sep}test{sep}test_5_circle_fourier_bg_layer1.glsl",
            "LAYER2": f"{GLSL_DIR}{sep}test{sep}test_5_circle_fourier_bg_layer2.glsl",
            "LAYER2PFX": f"{GLSL_DIR}{sep}test{sep}test_5_circle_fourier_bg_layer2_pfx.glsl",
            "LAYER_PARTICLES": f"{GLSL_DIR}{sep}test{sep}test_5_circle_fourier_bg_layer_particles.glsl",
            "BACKGROUND": f"{ASSETS_DIR}{sep}free_assets{sep}glsl_default_background.jpg",
            # "LOGO": f"{ASSETS_DIR}{sep}free_assets{sep}mmv_logo.png",
            "LOGO": f"{ASSETS_DIR}{sep}free_assets{sep}mmv_logo_alt_white.png",
        }
    }
}

# # Render to video or view real time?
# mode = "render"
mode = "view"

# Input audio source
RENDER_MODE_AUDIO_FILE = f"{ASSETS_DIR}{sep}free_assets{sep}kawaii_bass.ogg"

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
        sample_rate = SAMPLERATE,
        do_calculate_fft = CALCULATE_FFT
    )

    # Read source audio file
    source.init(path = RENDER_MODE_AUDIO_FILE)

    # Micro
    DURATION = source.duration
 
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
        DURATION, # duration
        FRAMERATE, # fps
        DURATION * FRAMERATE, # frame count
        50 # max images on buffer to be piped
    )).start()

    # Increase this value to get more aggressiveness or just turn up the computer volume
    multiplier = 180

# Mode is to view real time
elif mode == "view":

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
    source.init(search_for_loopback = True)

    # source.capture_and_process_loop()
    source.start_async()

    # Increase this value to get more aggressiveness or just turn up the computer volume
    multiplier = 140

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

try:
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
        pipeline_info = source.info.copy()

        # # Temporary stuff

        # Amplitudes
        if "average_amplitudes" in pipeline_info.keys():
            smooth_audio_amplitude = smooth_audio_amplitude + (pipeline_info["average_amplitudes"][2] - smooth_audio_amplitude) * 0.054
            pipeline_info["smooth_audio_amplitude"] = smooth_audio_amplitude * multiplier 

            smooth_audio_amplitude2 = smooth_audio_amplitude2 + (pipeline_info["average_amplitudes"][2] - smooth_audio_amplitude2) * 0.08
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
            prevfft[index] = prevfft[index] + (value*multiplier - prevfft[index]) * 0.25

        # Write the FFT
        mgl.write_texture_pipeline(texture_name = "fft", data = prevfft.astype(np.float32))

        # DEBUG: print pipeline
        # print(pipeline_info)

        # Next iteration
        mgl.next(custom_pipeline = pipeline_info)

        # If we'll be rendering, write to the video encoder
        if mode == "render":
            mgl.read_into_subprocess_stdin(video_pipe.subprocess.stdin)
            print("Write", step, source.steps_per_loop)

            # Looped the audio one time, exit
            if source.loops == 1:
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

if mode == "view":
    source.stop()

# # Save first frame from the shader and quit

# if False:
#     img = Image.frombytes('RGB', mgl.window.fbo.size, mgl.read())
#     img.save('output.jpg')
#     exit()
