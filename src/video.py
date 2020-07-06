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

from functions import Functions
from PIL import Image
import subprocess
import copy
import time
import sys


class FFmpegWrapper():
    def __init__(self, context):
        self.context = context
        self.functions = Functions()

        # TODO: WINDWOWZ
        self.ffmpeg_binary = "ffmpeg"

    # Create a FFmpeg writable pipe for generating a video
    def pipe_one_time(self, output):

        debug_prefix = "[FFmpegWrapper.pipe_one_time]"

        command = [
                self.ffmpeg_binary,
                '-loglevel', 'panic',
                '-nostats',
                '-hide_banner',
                '-y',
                '-r', str(self.context.fps),
                '-f', "image2pipe",
                '-i', '-',
                '-i', self.context.input_file,
                #'-an',
                '-c:v', 'libx264',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-r', str(self.context.fps),
                output
        ]

        self.pipe_subprocess = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

        print(debug_prefix, "Open one time pipe")

        self.stop_piping = False
        self.lock_writing = False
        self.images_to_pipe = []

    # Write images into pipe
    def write_to_pipe(self, image):
        self.images_to_pipe.append(copy.deepcopy(image.image_array()))

    # http://stackoverflow.com/a/9459208/284318
    def pure_pil_alpha_to_color_v2(self, image, color=(0, 0, 0)):
        image.load()
        background = Image.new('RGB', image.size, color)
        background.paste(image, mask=image.split()[3])
        return background

    # Thread save the images to the pipe, this way processing.py can do its job while we write the images
    def pipe_writer_loop(self):

        debug_prefix = "[FFmpegWrapper.pipe_writer_loop]"

        count = 0
        
        start = time.time()

        while not self.stop_piping:
            if len(self.images_to_pipe) > 0:
                self.lock_writing = True
                image = self.images_to_pipe.pop(0).convert("RGB")
                # image = self.pure_pil_alpha_to_color_v2(image)
                image.save(self.pipe_subprocess.stdin, format="jpeg", quality=100)
                self.lock_writing = False
                count += 1
                current_time = round((1/self.context.fps) * count, 2)
                duration = round(self.context.duration, 2)
                remaining = duration - current_time
                now = time.time()
                took = now - start
                eta = round(self.functions.proportion(current_time, took, remaining) / 60, 2)
                
                print("Write to pipe, count=[%s] proc=[%.2f sec / %.2f sec] total=[%.2f min] eta=[%.2f min]" % (count, current_time, duration, round(took/60, 2), eta))
            else:
                time.sleep(0.1)

    # Close stdin and stderr of pipe_subprocess and wait for it to finish properly
    def close_pipe(self):

        debug_prefix = "[FFmpegWrapper.close_pipe]"

        print(debug_prefix, "Closing pipe")

        while not len(self.images_to_pipe) == 0:
            print(debug_prefix, "Waiting for image buffer list to end, len [%s]" % len(self.images_to_pipe))
            time.sleep(0.1)

        while self.lock_writing:
            print(debug_prefix, "Lock writing is on, should only have one image?")
            time.sleep(0.1)

        self.stop_piping = True
        self.pipe_subprocess.stdin.close()
        self.pipe_subprocess.stderr.close()

        print(debug_prefix, "Waiting process to finish")

        self.pipe_subprocess.wait()

        print(debug_prefix, "Closed!!")