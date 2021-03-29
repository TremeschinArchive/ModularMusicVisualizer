"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Carykh's JumpCutter (https://github.com/carykh/jumpcutter)
re-implementation by me, Tremeschin under MMV's code base for a few things:

1. Faster render speeds
2. No extracting video images to disk (only file is the processed audio)

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

debug_prefix = "[run_jumpcutter.py]"

from mmv.common.cmn_functions import Functions
from scipy.io.wavfile import write
from tqdm import tqdm
import numpy as np
import threading
import soundcard
import math
import time
import wave
import cv2
import sys
import os

def _(): pass

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
                    self.kflags[arg[0]] = '='.join(arg[1:])

                # Is a flag
                else:
                    self.flags.append(arg)

# Parse shell arguments TODO: proper interface using typer?
# Temporary file mostly?
args = ArgParser(sys.argv)

# List and override soundcard outputs
if ("list" in args.flags):
    print(f"{debug_prefix} Available devices to play audio:")
    for index, device in enumerate(soundcard.all_speakers()):
        print(f"{debug_prefix} > ({index}) [{device.name}]")
    print(f"{debug_prefix} :: Run this script again with [play=N] flag to override")
    sys.exit(0)
    
# Overriding capture stuff
output_sound_card = args.kflags.get("play", None)
override_record_device = None

if output_sound_card is not None:
    recordable = soundcard.all_speakers()

    # Error assertion
    if (len(recordable) < int(cap)) or (int(cap) < 0):
        raise RuntimeError(f"Target play device is out of bounds [{cap}] out of (0, {len(recordable)})")

    # Get the device
    for index, device in enumerate(recordable):
        if index == int(cap):
            override_record_device = device
            break
else:
    output_sound_card = soundcard.default_speaker()

# Append previous folder to path, debug prefix
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(THIS_DIR + "/../")
sys.path.append("..")
sep = os.path.sep

# Import mmv, get interface
import mmv
interface = mmv.MMVPackageInterface()

# # Externals

# Video encoder (will only auto download for Windows)
interface.check_download_externals(target_externals = ["ffmpeg"])

# # Audio File

# Dirs
GLSL_DIR = f"{interface.data_dir}{sep}glsl"
GLSL_INCLUDE_FOLDER = f"{GLSL_DIR}{sep}include"
ASSETS_DIR = f"{interface.assets_dir}"

# User
OFMT = args.kflags.get('ofmt', None)


# Both modes accepts this
INPUT_AUDIO_FILE = args.kflags.get("audio", None)
INPUT_VIDEO_FILE = args.kflags.get("video", None)

FINAL_OUTPUT = args.kflags.get("o", None)

# Assume some ofmt
if OFMT == None:
    if (INPUT_AUDIO_FILE != None) and (INPUT_VIDEO_FILE != None):
        OFMT = "video"
    elif (INPUT_AUDIO_FILE != None) and (INPUT_VIDEO_FILE == None):
        OFMT = "audio"
    elif (INPUT_AUDIO_FILE == None) and (INPUT_VIDEO_FILE != None):
        OFMT = "video"
    elif (INPUT_AUDIO_FILE == None) and (INPUT_VIDEO_FILE == None):
        raise RuntimeError("No video or audio input was set")

    print(f"{debug_prefix} Guessed [OFMT={OFMT}]")

# # Extract as needed

# # Jumpcutter config
SILENT_SPEED = float(args.kflags.get("silent", 10))
SOUNDED_SPEED = float(args.kflags.get("sounded", 1))
SILENT_THRESHOLD = float(args.kflags.get("threshold", 0.015))

if (INPUT_AUDIO_FILE == None) and (INPUT_VIDEO_FILE != None):
    INPUT_AUDIO_FILE = INPUT_VIDEO_FILE

# # Video capture, resolution

capture = cv2.VideoCapture(INPUT_VIDEO_FILE)
WIDTH = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
HEIGHT = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Multiplier of original resolution
FINAL_VIDEO_RES_MULTIPLIER = float(args.kflags.get("m", 0.0))

# If user send some multiplier then overrwide w and h
if FINAL_VIDEO_RES_MULTIPLIER != 0.0:
    FINAL_VIDEO_WIDTH = args.kflags.get("w", WIDTH)
    FINAL_VIDEO_HEIGHT = args.kflags.get("h", HEIGHT)
else:
    FINAL_VIDEO_WIDTH = WIDTH * float(FINAL_VIDEO_RES_MULTIPLIER)
    FINAL_VIDEO_HEIGHT = HEIGHT * float(FINAL_VIDEO_RES_MULTIPLIER)

# Frame rate, audio
ORIGINAL_FRAMERATE = float(capture.get(cv2.CAP_PROP_FPS))
RENDER_FRAMERATE = float(args.kflags.get("fps", ORIGINAL_FRAMERATE))
AUDIO_BATCH_SIZE = int(args.kflags.get("batch", 2048))

# Jumpcutter
jumpcutter = interface.get_jumpcutter()

# Configure with stuff
jumpcutter.configure(
    batch_size = AUDIO_BATCH_SIZE,
    sample_rate = 48000,
    target_fps = ORIGINAL_FRAMERATE,
)

# Read source audio file
jumpcutter.init(audio_path = INPUT_AUDIO_FILE)

mode = args.kflags.get("mode", "render")

# Stuff we'll need
functions = Functions()

if mode == "view":
    shader_interface = interface.get_shader_interface()
    mgl = shader_interface.get_mgl_interface(master_shader = True, flip = True)

    MSAA = 8

    # # MGL bootstrap

    # Set up target render configuration
    mgl.target_render_settings(
        width = WIDTH,
        height = HEIGHT,
        ssaa = 1,
        fps = ORIGINAL_FRAMERATE,
    )

    # Add directories for including #pragma include
    mgl.include_dir(GLSL_INCLUDE_FOLDER)
    mgl.mode(window_class = "headless", strict = True, vsync = False, msaa = MSAA)
    
    # Load the shader
    mgl.load_shader_from_path(
        fragment_shader_path = f"{interface.data_dir}{sep}glsl{sep}extensions{sep}jumpcutter.glsl",
        save_shaders_path = interface.runtime_dir,
        replaces = {
            "HEIGHT": HEIGHT,
            "WIDTH": WIDTH,
        },
    )

    with output_sound_card.player(samplerate = jumpcutter.sample_rate, channels = 2) as play_audio_stream:
        mgl.mode(window_class = "glfw", vsync = False, msaa = MSAA, strict = False)
        
        counter = 0
        while True:
            while jumpcutter.usable_up_to == counter:
                time.sleep(0.01)
            play_audio_stream.play(jumpcutter.info["playback_audios"][counter]["data"].T)
            counter += 1

if mode == "render":
    
    # For encoding to audio file
    audio_encoder_raw_to_file = interface.get_ffmpeg_wrapper()

    if OFMT == "video":
        print(f"{debug_prefix} Merging to temporary audio then rendering video")
        FINAL_AUDIO_FILE = F"{interface.runtime_dir}{sep}temp_jumpcutter_audio.mp3"
    if OFMT == "audio":
        print(f"{debug_prefix} Merging to final audio")
        FINAL_AUDIO_FILE = FINAL_OUTPUT

    info_on_audio_file = {}

    def thread_encode_to_audio():
        global jumpcutter, info_on_audio_file

        # Configure audio encoder
        audio_encoder_raw_to_file.raw_audio_to_file(
            sample_rate = jumpcutter.sample_rate,
            output_file = FINAL_AUDIO_FILE
        )

        # Start audio encoder
        audio_encoder_raw_to_file.start()

        for index, info in enumerate(jumpcutter.start(
            silent_speed = SILENT_SPEED,
            sounded_speed = SOUNDED_SPEED,
            silent_threshold = SILENT_THRESHOLD,
        )):
            if info["type"] == "deformation":
                info_on_audio_file[len(info_on_audio_file)] = info.copy()
                print(info["deformation_point"])

            # Write to audio file
            elif info["type"] == "raw_pcm":
                value = info.pop("data")
                audio_encoder_raw_to_file.subprocess.stdin.write(value.reshape(-1, order = "F"))
    
        # Close the audio encoder
        audio_encoder_raw_to_file.subprocess.stdin.close()

    audio_encode_thread = threading.Thread(target = thread_encode_to_audio, daemon = True)
    audio_encode_thread.start()
    audio_encode_thread.join()

    # Warn final audio is done
    if OFMT == "audio":
        print(f"{debug_prefix} Done!! Final audio only is rendered")
        audio_encode_thread.join()

    # Only continue if to render video
    if OFMT == "video":

        # # Read images, pipe, update, render

        PARTIAL_PIPE_VIDEO = f"[JumpCutter Video Only] {FINAL_OUTPUT}"

        # Video encoder
        ffmpeg = interface.get_ffmpeg_wrapper()
        ffmpeg.configure_encoding(
            width = WIDTH, height = HEIGHT,
            input_audio_source = None,
            input_video_source = "pipe",
            output_video = PARTIAL_PIPE_VIDEO,
            pix_fmt = "bgr24",
            framerate = ORIGINAL_FRAMERATE,
            preset = "slow",
            crf = 23,
            hwaccel = "auto", loglevel = "panic", nostats = True, hide_banner = True, opencl = False,
            tune = "stillimage", vflip = False, vcodec = "libx264", override = True,
        )
        ffmpeg.start()

        # # Progress bar
        progress_bar = tqdm(
            total = jumpcutter.total_steps,
            unit = " deformations",
            dynamic_ncols = True,
            colour = '#38bed6',
            position = 0,
            smoothing = 0.1,
        )
        progress_bar.set_description("Rendering Final JumpCutter Video")
        ok, frame = capture.read()

        # Output video timings
        seconds_per_frame = (1 / ORIGINAL_FRAMERATE)
        expect_new_frame = 0
        walked = 0

        # Iterate over all expected frames
        for step in range(jumpcutter.total_steps - 1):
            progress_bar.update(1)

            # Update the total based on how many audio splits were concatenated
            progress_bar.total = jumpcutter.total_steps - jumpcutter.not_flipped

            # Check we ended since we concatenate speeded or sounded parts together
            if (jumpcutter.finished) and (step == (jumpcutter.total_steps - 1 - jumpcutter.not_flipped)):
                break

            # Wait until we have the next point info
            while not (step + 1 in info_on_audio_file.keys()):
                time.sleep(0.01)

            # Deformation points are points such that the values (x, y) represent
            # respectively the output video time (x) and where to get on the original
            # video time (y) this current frame.
            this_deformation_point = info_on_audio_file[step]["deformation_point"]
            next_deformation_point = info_on_audio_file[step + 1]["deformation_point"]

            # Too short, the deformation points didn't catch up with the output video's expected
            # where to get a new frame in seconds
            if expect_new_frame > next_deformation_point[0]:
                continue
            
            # We loop until we finish this audio slice of region (until we overshoot
            # the other point's x value) 
            while expect_new_frame < next_deformation_point[0]:

                # Calculate linear interpolation between the two points we're expecting a new frame
                deformed_expect_frame = functions.lerp(this_deformation_point, next_deformation_point, expect_new_frame)

                # Until we didn't walk until the expected frame time, discard frames
                while walked <= deformed_expect_frame:
                    ok, frame = capture.read()
                    walked += seconds_per_frame

                # Write to the final video, add to the expected frame
                if ok:  # If we have a frame, write it (we can be on the video's end)           
                    ffmpeg.subprocess.stdin.write(frame)
                expect_new_frame += seconds_per_frame
            

        #   #   # Progress bar stuff
        progress_bar.close()
        #   #   #

        # Wait until audio is ready and concatenate into final output video
        audio_encode_thread.join()

        # Concatenate both video and audio
        ffmpeg.concatenate_video_and_audio(video = PARTIAL_PIPE_VIDEO, audio = FINAL_AUDIO_FILE, output = FINAL_OUTPUT)
    
        # Remove video only footage
        interface.utils.rmfile(PARTIAL_PIPE_VIDEO)
