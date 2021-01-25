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

# mgl.construct_shader()

mgl.construct_shader(fragment_shader = f"""\
#pragma map otherglsl=shader:{THIS_DIR}/test_otherglsl.glsl:1920x1080;
void main() {{

    // The ratio relative to the Y coordinate, we expand on X
    float resratio = (mmv_resolution.y / mmv_resolution.x);

    // OpenGL and Shadertoy UV coordinates, GL goes from -1 to 1 on every corner
    // and Shadertoy uses bottom left = (0, 0) and top right = (1, 1).
    // glub and stuv are normalized relative to the height of the screen, they are
    // respective the Opengl UV and Shadertoy UV you can use
    vec2 gluv = opengl_uv;
    vec2 stuv = shadertoy_uv;

    vec4 col = vec4( smoothstep(0.99, 1.0, stuv.x), abs(sin(2.343*mmv_time)), gluv.y, 1.0);
    vec4 otherglsl_color = texture(otherglsl, shadertoy_uv);

    fragColor = mix(col, otherglsl_color, stuv.y);
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

try:
    while True:
        mgl.next()
        n += 1
        
        # img = Image.frombytes('RGB', mgl.fbo.size, mgl.read())
        # img.save('output.jpg')
        # exit()

        video_pipe.write_to_pipe(n, mgl.read())


        # print(n / (time.time() - start))
except KeyboardInterrupt:
    video_pipe.subprocess.kill()
except BrokenPipeError:
    video_pipe.subprocess.kill()
