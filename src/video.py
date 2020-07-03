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

from PIL import Image
import subprocess
import time
import sys


class FFmpegWrapper():
    def __init__(self, context):
        self.context = context        
        self.ffmpeg_binary = "ffmpeg"

    def pipe_one_time(self, output):

        debug_prefix = "[FFmpegWrapper.pipe_one_time]"

        command = [
                self.ffmpeg_binary,
                '-loglevel', 'panic',
                '-nostats',
                '-hide_banner',
                '-y',
                '-f', "image2pipe",
                '-i', '-',
                '-an',
                '-c:v', 'libx264',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-r', self.context.fps,
                output
        ]

        self.pipe_subprocess = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

        print(debug_prefix, "Open one time pipe")
