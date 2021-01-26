"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Test unit for the upcoming MMVShaderMGL

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
import threading
import random
import time
import sys
import os


# Append previous folder to path
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append("..")
sys.path.append(
    THIS_DIR + "/../"
)

# Import mmv, get interface
import mmv
interface = mmv.MMVPackageInterface()
shader_interface = interface.get_shader_interface()
mgl = shader_interface.get_mgl_interface()

# WIDTH = 1280
# HEIGHT = 720
WIDTH = 1920
HEIGHT = 1080
FRAMERATE = 60
DURATION = 30

# Set up target render configuration
mgl.render_config(
    width = WIDTH,
    height = HEIGHT,
    fps = FRAMERATE,
)

# Directories
sep = os.path.sep
GLSL_FOLDER = f"{interface.data_dir}{sep}glsl"
GLSL_INCLUDE_FOLDER = f"{GLSL_FOLDER}{sep}include"

# Add directories for including #pragma include
mgl.include_dir(GLSL_INCLUDE_FOLDER)

# Load the test 1 shader
mgl.load_shader_from_path(
    fragment_shader_path = f"{GLSL_FOLDER}{sep}test{sep}test_1_simple_shader.glsl"
)

# Want to encode video set ffmpeg, preview realtime set ffplay
# ff = "ffmpeg"
ff = "ffplay"


if ff == "ffplay":
    # Get the FFplay wrapper
    video_pipe = interface.get_ffplay_wrapper()

    # Configure it on what we expect , width height and framerate
    video_pipe.configure(
        ffplay_binary_path = interface.find_binary("ffplay"),
        width = WIDTH,
        height = HEIGHT,
        pix_fmt = "rgb24",
        vflip = False,
        framerate = 6000,
    )

    threading.Thread(target = video_pipe.pipe_writer_loop, daemon = True).start()

    # Start the FFplay subprocess
    video_pipe.start()

elif ff == "ffmpeg":
   
    video_pipe = interface.get_ffmpeg_wrapper()
    video_pipe.configure_encoding(
        ffmpeg_binary_path = interface.find_binary("ffmpeg"),
        width = WIDTH,
        height = HEIGHT,
        input_audio_source = None,
        input_video_source = "pipe",
        output_video = "ofshader.mkv",
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

    threading.Thread(target = video_pipe.pipe_writer_loop, args = (
        DURATION, # duration
        FRAMERATE, # fps
        DURATION * FRAMERATE,
        50

    )).start()


try:
    start = time.time()
    n = -1  # Iteration counter
    fps_last_n = 120
    times = [time.time() for _ in range(fps_last_n)]

    # Main test routine
    while True:

        # Next iteration
        mgl.next(custom_pipeline = {})
        
        # Save first frame from the shader and quit
        if False:
            img = Image.frombytes('RGB', mgl.fbo.size, mgl.read())
            img.save('output.jpg')
            exit()

        # video_pipe.write_to_pipe(n, mgl.read())
        mgl.read_into_subprocess_stdin(video_pipe.subprocess.stdin)

        # Print FPS, well, kinda, the average of the last fps_last_n frames
        times[n % fps_last_n] = time.time()
        print(f":: Average FPS last ({fps_last_n} frames): [{round(fps_last_n / (max(times) - min(times)), 1)}] \r", end = "", flush = True)
        n += 1

# Except user ctrl-c's or closes the FFplay pipe: window we kill the subprocess
# otherwise we'll have many idle FFplay subprocesses on the system

except KeyboardInterrupt:
    video_pipe.subprocess.kill()
except BrokenPipeError:
    video_pipe.subprocess.kill()
