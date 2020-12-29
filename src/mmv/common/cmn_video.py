"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Deals with Video related stuff, also a FFmpeg wrapper in its own class

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
import mmv.common.cmn_any_logger
from PIL import Image
import numpy as np
import subprocess
import logging
import copy
import time
import sys
import cv2


class FFmpegWrapper:

    # Create a FFmpeg writable pipe for generating a video
    # For more detailed info see [https://trac.ffmpeg.org/wiki/Encode/H.264]
    def pipe_images_to_video(self, 
        ffmpeg_binary_path: str,  # Path to the ffmpeg binary
        width: int,
        height: int,
        input_audio_file: str,  # Path
        output_video: str, # Path
        pix_fmt: str,  # rgba, rgb24, bgra
        framerate: int,
        preset: str = "slow",  # libx264 ffmpeg preset
        hwaccel = "auto",  # Try utilizing hardware acceleration? None ignores this flag
        opencl: bool = False,  # Add -x264opts opencl ?
        dumb_player: bool = True,  # Add -vf format=yuv420p for compatibility
        crf: int = 17,  # Constant Rate Factor [0: lossless, 23: default, 51: worst] 
        vcodec: str = "libx264",  # Encoder library, libx264 or libx265
        override: bool = True,  # Do override the target output video if it exists?
        depth = LOG_NO_DEPTH,
    ) -> None:

        debug_prefix = "[FFmpegWrapper.pipe_images_to_video]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Generate the command for piping images to
        ffmpeg_pipe_command = [
            ffmpeg_binary_path
        ]

        # Add hwaccel flag if it's set
        if hwaccel is not None:
            ffmpeg_pipe_command += ["-hwaccel", hwaccel]

        # Add the rest of the command
        ffmpeg_pipe_command += [
            "-loglevel", "panic",
            "-nostats",
            "-hide_banner",
            "-f", "rawvideo",
            # "-vcodec", "rawvideo",
            "-pix_fmt", pix_fmt,
            "-r", f"{framerate}",
            "-s", f"{width}x{height}",
            "-i", "-",
            "-i", input_audio_file,
            "-c:v", f"{vcodec}",
            "-preset", preset,
            "-r", f"{framerate}",
            "-crf", f"{crf}",
            "-c:a", "copy",
        ]

        # Compatibility mode
        if dumb_player:
            ffmpeg_pipe_command += ["-vf", "format=yuv420p"]

        # Add opencl to x264 flags?
        if opencl:
            ffmpeg_pipe_command += ["-x264opts", "opencl"]
   
        # Add output video
        ffmpeg_pipe_command += [output_video]

        # Do override the target output video
        if override:
            ffmpeg_pipe_command.append("-y")

        # Log the command for generating final video
        logging.info(f"{depth}{debug_prefix} FFmpeg command is: {ffmpeg_pipe_command}")
        logging.info(f"{depth}{debug_prefix} Starting FFmpeg pipe subprocess..")

        # Create a subprocess in the background
        self.pipe_subprocess = subprocess.Popen(
            ffmpeg_pipe_command,
            stdin  = subprocess.PIPE,
            stdout = subprocess.PIPE,
        )

        print(debug_prefix, "Open one time pipe")

        self.stop_piping = False
        self.lock_writing = False
        self.images_to_pipe = {}

    # Write images into pipe, run pipe_writer_loop first!!
    def write_to_pipe(self, index, image):
        while len(list(self.images_to_pipe.keys())) >= self.max_images_on_pipe_buffer:
            print("Too many images on pipe buffer")
            time.sleep(0.1)

        self.images_to_pipe[index] = image
        del image

    # Thread save the images to the pipe, this way processing.py can do its job while we write the images
    def pipe_writer_loop(self, duration_seconds: float, fps: float, frame_count: int, max_images_on_pipe_buffer: int):
        debug_prefix = "[FFmpegWrapper.pipe_writer_loop]"

        self.max_images_on_pipe_buffer = max_images_on_pipe_buffer
        self.count = 0

        while not self.stop_piping:
            if self.count in list(self.images_to_pipe.keys()):
                if self.count == 0:
                    start = time.time()
                
                # We're writing stuff
                self.lock_writing = True

                # Get the next image from the list as count is on the images to pipe dictionary keys
                image = self.images_to_pipe.pop(self.count)

                # Pipe the numpy RGB array as image
                self.pipe_subprocess.stdin.write(image)

                # Finished writing
                self.lock_writing = False

                # Are we finished on the expected total number of images?
                if self.count == frame_count - 1:
                    self.close_pipe()
                
                self.count += 1

                # Stats
                current_time = (self.count / fps)   # Current second we're processing
                propfinished = ((current_time + (1/fps)) / duration_seconds) * 100  # Overhaul percentage completion
                remaining = duration_seconds - current_time  # How much seconds left to produce
                now = time.time()
                took = now - start  # Total time took in this runtime
                eta = (took * remaining) / current_time

                # Convert to minutes
                took /= 60
                eta /= 60
                took_plus_eta = took + eta

                took_plus_eta = f"{int(took_plus_eta)}m:{(took_plus_eta - int(took_plus_eta))*60:.0f}s"
                took = f"{int(took)}m:{(took - int(took))*60:.0f}s"
                eta = f"{int(eta)}m:{(eta - int(eta))*60:.0f}s"

                print(f"\rProgress=[Frame: {self.count} - {current_time:.2f}s / {duration_seconds:.2f}s = {propfinished:0.2f}%] Took=[{took}] ETA=[{eta}] EST Total=[{took_plus_eta}]", end="")
            else:
                time.sleep(0.1)
        
        self.pipe_subprocess.stdin.close()

    # Close stdin and stderr of pipe_subprocess and wait for it to finish properly
    def close_pipe(self):

        debug_prefix = "[FFmpegWrapper.close_pipe]"

        print(debug_prefix, "Closing pipe")

        # Wait for all images to be piped, noted: the last one will still be there because of .pop and
        # will have a false signal of images to pipe being empty, we correct on the next loop
        while not len(self.images_to_pipe.keys()) == 0:
            print(debug_prefix, "Waiting for image buffer list to end, len [%s]" % len(self.images_to_pipe))
            time.sleep(0.1)

        # Is there any more images left to pipe? ie, are we holding one image on memory and piping to ffmpeg
        while self.lock_writing:
            print(debug_prefix, "Lock writing is on, should only have one image?")
            time.sleep(0.1)

        self.stop_piping = True

        print(debug_prefix, "Stopped pipe!!")

