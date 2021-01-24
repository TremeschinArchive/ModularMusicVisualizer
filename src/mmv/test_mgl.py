from PIL import Image
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

mgl.render_config(
    width = WIDTH,
    height = HEIGHT,
    fps = FRAMERATE,
)

mgl.construct_shader()

mgl.construct_shader(fragment_shader = f"""\
#pragma map tex=image:{THIS_DIR}/___image.png:1920x1080
#pragma map otherglsl=shader:/{THIS_DIR}/__otherglsl.glsl:1920x1080;

void main() {{
    float screen_ratio_x = mmv_resolution.x / mmv_resolution.y;
    vec2 uv_transformed = uv;
    uv_transformed.x *= screen_ratio_x;

    // fragColor = vec4(uv.x, uv.y, 0.0, 0.0);
    vec2 flipped_uv = uv;
    // flipped_uv.y *= -1;
    fragColor = texture(otherglsl, flipped_uv);
    // fragColor = texture(tex, uv);
    // fragColor = vec4(uv.x, uv.y, abs(sin(mmv_time/180.0)), 1.0);
}}""")


# ff = "ffmpeg"
ff = "ffplay"

import threading

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


import time
start = time.time()
n = -1

while True:
    mgl.next()
    n += 1
    
    # img = Image.frombytes('RGB', mgl.fbo.size, mgl.read())
    # img.save('output.jpg')
    # exit()

    video_pipe.write_to_pipe(n, mgl.read())

    print(n / (time.time() - start))
