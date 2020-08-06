"""
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

from mmv.common.cmn_functions import Functions
from mmv.common.cmn_types import *
from PIL import Image
import numpy as np
import subprocess
import ffmpeg
import copy
import time
import sys
import cv2


class FFmpegWrapper():
    def __init__(self, context, controller):
        self.context = context
        self.controller = controller
        self.functions = Functions()

    # Create a FFmpeg writable pipe for generating a video
    def pipe_one_time(self, output):

        debug_prefix = "[FFmpegWrapper.pipe_one_time]"

        self.pipe_subprocess = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='rgba', r=self.context.fps, s='{}x{}'.format(self.context.width, self.context.height))
            .output(output, pix_fmt='yuv420p', vcodec='libx264', r=self.context.fps, crf=18, loglevel="quiet")
            .global_args('-i', self.context.input_file)
            .overwrite_output()
            .run_async(pipe_stdin=True)
        )

        print(debug_prefix, "Open one time pipe")

        self.stop_piping = False
        self.lock_writing = False
        self.images_to_pipe = {}

    # Write images into pipe
    def write_to_pipe(self, index, image):
        while len(list(self.images_to_pipe.keys())) >= 20:
            print("Too many images on pipe buffer")
            time.sleep(0.1)

        self.images_to_pipe[index] = image
        del image

    # Thread save the images to the pipe, this way processing.py can do its job while we write the images
    def pipe_writer_loop(self, duration_seconds: Number):

        debug_prefix = "[FFmpegWrapper.pipe_writer_loop]"

        self.count = 0

        while not self.stop_piping:
            if self.count in list(self.images_to_pipe.keys()):
                if self.count == 0:
                    start = time.time()
                
                # We're writing stuff
                self.lock_writing = True

                # Get the next image from the list as count is on the images to pipe dictionary keys
                image = self.images_to_pipe.pop(self.count)

                # If user set to watch the realtime video, convert RGB numpy array to BGR cv2 image
                if self.context.watch_processing_video_realtime and self.count > 0:
                    cvimage = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    cv2.imshow("Current piped frame", cvimage)
                    cv2.waitKey(1)

                # Pipe the numpy RGB array as image
                self.pipe_subprocess.stdin.write(image)

                # Finished writing
                self.lock_writing = False

                # Are we finished on the expected total number of images?
                if self.count == self.controller.total_steps - 1:
                    self.close_pipe()
                
                self.count += 1

                # Stats
                current_time = round((1/self.context.fps) * self.count, 2)  # Current second we're processing
                duration = round(duration_seconds, 2)  # Total duration in seconds
                remaining = duration - current_time  # How much seconds left to produce
                now = time.time()
                took = now - start  # Total time took in this runtime
                eta = round(self.functions.proportion(current_time, took, remaining) / 60, 2)
                
                print("Frame count=[%s] proc=[%.2f sec / %.2f sec] took=[%.2f min] eta=[%.2f min] sum=[%.2f min] fullpower=[%s]" % (self.count, current_time, duration, round(took/60, 2), eta, round((took/60 + eta), 2), not self.controller.core_waiting))
            else:
                time.sleep(0.1)

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

