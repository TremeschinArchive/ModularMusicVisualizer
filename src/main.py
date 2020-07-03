"""
===============================================================================

Purpose: Abstract, wrap, connect other files

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

from mmvanimation import MMVAnimation
from video import FFmpegWrapper
from utils import Miscellaneous
from fourier import Fourier
from context import Context
from canvas import Canvas
from assets import Assets
from audio import Audio
from frame import Frame
from PIL import Image
import numpy as np
import argparse
import math


class MMV():
    def __init__(self, args):

        debug_prefix = "[MMV.__init__]"

        print(debug_prefix, "Creating Context()")
        self.context = Context()
        # self.context.reset_directories()

        print(debug_prefix, "Creating Canvas()")
        self.canvas = Canvas(self.context)

        print(debug_prefix, "Creating Assets()")
        self.assets = Assets(self.context)

        print(debug_prefix, "Creating Fourier()")
        self.fourier = Fourier()

        print(debug_prefix, "Creating FFmpegWrapper()")
        self.ffmpeg = FFmpegWrapper()

        self.context.input_file = args["input_file"]

        print(debug_prefix, "Making Directories")
        self.context.utils.mkdir_dne(
            self.context.processing
        )

        print(debug_prefix, "Creating Audio()")
        self.audio = Audio(self.context)

        print(debug_prefix, "Reading Audio")
        self.audio.read(self.context.input_file)

        print(debug_prefix, "Creating MMVAnimation()")
        self.mmvanimation = MMVAnimation(self.context)

        # # #

        # Start the pipe one time
        #self.ffmpeg.pipe_one_time()

        self.assets.pygradienter("particles", 100, 100, 1)

        self.mmvanimation.generate()

        self.mmvanimation.next()

        # self.canvas.canvas.save("canvas.jpg")



        '''
        self.context.nbatches = len(self.audio.data[0]) // self.context.batch_size
        vertical_points = 256

        canvas = np.zeros([vertical_points, self.context.nbatches, 3], dtype=np.uint8)

        for batch in range(self.context.nbatches):
            fft = self.fourier.fft(
                self.audio.data[0][
                    self.context.batch_size * batch
                    :
                    self.context.batch_size * (batch + 1)
                ],
                self.audio.info
            )

            def prop(a, b, c):
                # a - b
                # c - x
                # x = b*c/a
                return b*c/a

            def transformation(y):
                
                p = prop(vertical_points, 1, y)
                k = p**2
                return y*k

                # return vertical_points**(y/vertical_points)
                """
                x**agressiveness = vertical_points
                """
                # r = math.log(y+1, vertical_points)*vertical_points
                # print(y, r)
                # print("trans", y, r)

            lenfft = len(fft)
            chunksize = (lenfft/vertical_points)

            print(chunksize)

            for index in range(vertical_points):

                position = vertical_points - index - 1
                index = int(transformation(index))

                chunk = fft[
                    int(chunksize * index)
                    :
                    int(chunksize * (index + 1))
                ]

                l = len(chunk)

                if not l == 0:
                    size = (sum(abs(chunk)) / len(chunk))
                else:
                    size = 0

                # print("size", size)

                if size < 20:
                    size = size * 20
                    if size > 255:
                        size = 255

                canvas[position][batch][0] = size
                canvas[position][batch][1] = size
                canvas[position][batch][2] = size
        '''
        '''
            chunks = np.array_split(fft, vertical_points)

            for index, chunk in enumerate(chunks):
                size = (sum(abs(chunk)) / len(chunk)) * 4
                # print("Chunk r:", chunk.real)
                # print("Chunk:", chunk)
                # print("Size:", size)
                index = int(math.log(index+1)*128)
                canvas[index][batch][0] = size
                canvas[index][batch][1] = size
                canvas[index][batch][2] = size
        '''


        #print(fft)


if __name__ == "__main__":

    # Greeter message :)
    Miscellaneous()
    
    # Create ArgumentParser
    args = argparse.ArgumentParser(description='Argu    ments for Modular Music Visualizer')

    # Add arguments
    args.add_argument('-i', '--input_file', required=True, help="(string) Input audio to generate final video, if not .wav uses ffmpeg to convert")
    args.add_argument("-p", "--profile", required=False, help="(string) Generate the video with that profile script under profiles dir")

    # Parse and organize the arguments
    args = args.parse_args()
    args = {
        "input_file": args.input_file,
        "profile": args.profile,
    }

    MMV(args)
