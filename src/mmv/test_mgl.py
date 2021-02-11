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


# Append previous folder to path
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)

# Prefix
debug_prefix = "[test_mgl.py]"

# Import mmv, get interface
import mmv
interface = mmv.MMVPackageInterface()
shader_interface = interface.get_shader_interface()
mgl = shader_interface.get_mgl_interface(master_shader = True)

WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60
SAMPLERATE = 48000
CALCULATE_FFT = True
MSAA = 8

# Set up target render configuration
mgl.target_render_settings(
    width = WIDTH,
    height = HEIGHT,
    fps = FRAMERATE,
)

# Render to video or view real time?
# mode = "render"
mode = "view"

if mode == "render":
    mgl.mode(
        window_class = "headless",
        strict = True,
        msaa = MSAA,
    )

elif mode == "view":
    mgl.mode(
        window_class = "glfw",
        vsync = False,
        msaa = MSAA,
        strict = False,
    )

    # # Realtime Audio

    # Search for loopback, configure
    source = interface.get_audio_source_realtime()
    source.init(search_for_loopback = True)
    source.configure(
        batch_size = 2048 * 4 * 2,
        sample_rate = SAMPLERATE,
        recorder_numframes = int(SAMPLERATE / (FRAMERATE / 2)),  # Safety: expect half of fps
        calculate_fft = CALCULATE_FFT
    )
    source.audio_processing.configure(config_dict = {
        # 0: {
        #     "sample_rate": 1000,
        #     "start_freq": 20,
        #     "end_freq": 500,
        # },
        # 1: {
        #     "sample_rate": 40000,
        #     "start_freq": 500,
        #     "end_freq": 20000,
        # }

        1: {
            "sample_rate": 48000,
            "start_freq": 30,
            "end_freq": 20000,
        }
    })
    MMV_FFTSIZE = source.audio_processing.FFT_length
    print(f"{debug_prefix} FFT Size on AudioProcessing is [{MMV_FFTSIZE}]")
    
    # source.capture_and_process_loop()
    source.start_async()

# Directories
sep = os.path.sep
GLSL_FOLDER = f"{interface.data_dir}{sep}glsl"
GLSL_INCLUDE_FOLDER = f"{GLSL_FOLDER}{sep}include"

# Add directories for including #pragma include
mgl.include_dir(GLSL_INCLUDE_FOLDER)

# Which test to run?
test_number = 4
tests = {
    1: {"frag": f"{GLSL_FOLDER}{sep}test{sep}test_1_simple_shader.glsl"},
    2: {"frag": f"{GLSL_FOLDER}{sep}test{sep}___test_2_post_fx_png.glsl"},
    3: {"frag": f"{GLSL_FOLDER}{sep}test{sep}test_3_rt_audio.glsl"},
    4: {"frag": f"{GLSL_FOLDER}{sep}test{sep}test_4_fourier.glsl"},
}

# Load the shader from the path
cfg = tests[test_number]
mgl.load_shader_from_path(
    fragment_shader_path = cfg["frag"],
    replaces = {
        "MMV_FFTSIZE": MMV_FFTSIZE,
    },
    save_shaders_path = interface.runtime_dir
)

# Get a video encoder
if mode == "render":
    raise NotImplementedError

    video_pipe = interface.get_ffmpeg_wrapper()
    video_pipe.configure_encoding(
        ffmpeg_binary_path = interface.find_binary("ffmpeg"),
        width = WIDTH,
        height = HEIGHT,
        input_audio_source = None,
        input_video_source = "pipe",
        output_video = "rendered_shader.mkv",
        pix_fmt = "rgb24",
        framerate = FRAMERATE,
        preset = "veryfast",
        hwaccel = "auto",
        loglevel = "panic",
        nostats = True,
        hide_banner = True,
        opencl = False,
        crf = 17,
        tune = "film",
        vflip = False,
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

# # FPS calculation bootstrap
start = time.time()
n = -1  # Iteration counter
fps_last_n = 120
times = [time.time() + i/FRAMERATE for i in range(fps_last_n)]

# # Temporary pipeline calculations TODO: proper class

smooth_audio_amplitude = 0
prevfft = np.array([0.0 for _ in range(MMV_FFTSIZE)], dtype = np.float32)

# Increase this value to get more aggressiveness or just turn up the computer volume
multiplier = 6

# Main test routine
while True:

    # The time this loop is starting
    startcycle = time.time()

    # Calculate the fps
    fps = round(fps_last_n / (max(times) - min(times)), 1)
    
    # Info we pass to the shader, this is WIP and hacky rn
    pipeline_info = {}

    # We have:
    # - average_amplitudes: vec3 array, L, R and Mono
    pipeline_info = source.info

    # # Temporary stuff

    # Amplitudes
    if "average_amplitudes" in pipeline_info.keys():
        smooth_audio_amplitude = smooth_audio_amplitude + (pipeline_info["average_amplitudes"][2] - smooth_audio_amplitude) * 0.154
        pipeline_info["smooth_audio_amplitude"] = smooth_audio_amplitude * multiplier

    # If we have an fft key
    if "fft" in pipeline_info.keys():

        # Interpolation
        for index, value in enumerate(pipeline_info["fft"]):
            prevfft[index] = prevfft[index] + (value*multiplier - prevfft[index]) * 0.35

        # Write the FFT
        mgl.write_texture_pipeline(texture_name = "fft", data = prevfft.astype(np.float32))
        del pipeline_info["fft"]

    # DEBUG: print pipeline
    # print(pipeline_info)

    # Next iteration
    mgl.next(custom_pipeline = pipeline_info)
    mgl.update_window()

    # If we'll be rendering, write to the video encoder
    if mode == "render":
        mgl.read_into_subprocess_stdin(video_pipe.subprocess.stdin)

    elif mode == "view":
        # The window received close command
        if mgl.window_should_close:
            break

    # Print FPS, well, kinda, the average of the last fps_last_n frames
    times[n % fps_last_n] = time.time()
    print(f":: Average FPS last ({fps_last_n} frames): [{fps}] \r", end = "", flush = True)
    n += 1

    # Vsync (yea we really need this)
    if not mgl.vsync:
        while time.time() - startcycle < 1 / FRAMERATE:
            time.sleep(1 / (FRAMERATE * 100))
    
# # Save first frame from the shader and quit

# if False:
#     img = Image.frombytes('RGB', mgl.window.fbo.size, mgl.read())
#     img.save('output.jpg')
#     exit()
