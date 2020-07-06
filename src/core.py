"""
===============================================================================

Purpose: Wrap and execute every MMV class

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

from utils import Utils
import threading
import time
import os


class Core():
    def __init__(self, context, controller, canvas, assets, fourier, ffmpeg, audio, mmvanimation):
        # Get every class
        self.context = context
        self.controller = controller
        self.canvas = canvas
        self.assets = assets
        self.fourier = fourier
        self.ffmpeg = ffmpeg
        self.audio = audio
        self.mmvanimation = mmvanimation
        self.utils = Utils()

        self.ROOT = self.context.ROOT

    # Calls and starts threads 
    def start(self):

        debug_prefix = "[Core.start]"

        # Create the pipe write thread
        self.controller.threads["pipe_writer_loop"] = threading.Thread(target=self.ffmpeg.pipe_writer_loop)
        print(debug_prefix, "Created thread video.ffmpeg.pipe_writer_loop")
        
        # Start the threads, warn the user that the output is no more linear
        print(debug_prefix, "[WARNING] FROM NOW ON NO OUTPUT IS LINEAR AS THREADING STARTS")

        # For each thread, start them
        for thread in self.controller.threads:
            print(debug_prefix, "Starting thread: [\"%s\"]" % thread)
            self.controller.threads[thread].start()
        
        print(debug_prefix, "Started!!")

        self.run()

    def run(self):

        debug_prefix = "[Core.run]"

        # How many steps is the audio duration times the frames per second
        total_steps = int(self.context.duration * self.context.fps)

        print(debug_prefix, "Total steps:", total_steps)

        # Generate the assets
        self.assets.pygradienter("particles", 100, 100, 1)

        # Generate a Animation
        self.mmvanimation.generate()
        self.canvas.reset_canvas()

        # Next animation
        for this_step in range(0, total_steps):

            # Add the offset audio step (because interpolation isn't instant for smoothness)
            this_step += self.context.offset_audio_before_in_many_steps

            # If this step is out of bounds because the offset, set it to its max value
            if this_step >= total_steps - 1:
                this_step = total_steps - 1

            # The current time in seconds we're going to slice the audio based on its samplerate
            # If we offset to the opposite way, the starting point can be negative hence the max function.
            this_time = max( (1/self.context.fps) * this_step, 0 )

            # The current time in sample count to slice the audio
            this_time_sample = int(this_time * self.audio.info["sample_rate"])

            # The slice starts at the this_time_sample and end the cut here
            until = int(this_time_sample + self.context.batch_size)

            # Get the audio slice
            audio_slice = self.audio.data[0][this_time_sample:until]

            # Calculate the fft on the frequencies
            fft = self.fourier.fft(
                audio_slice,
                self.audio.info
            )

            # Process next animation with audio info and the step count to process on
            self.mmvanimation.next(audio_slice, fft, this_step)

            # Save current canvas's Frame to the final video
            self.ffmpeg.write_to_pipe(self.canvas.canvas)
            
            # Hard debug, save the canvas into a folder
            # self.canvas.canvas.save("data/canvas%s.png" % this_step)

            # [ FAILSAFE ] Reset the canvas (not needed if full background is present (recommended))
            self.canvas.reset_canvas()

        # We're out of animation steps, close the pipe to finish the video
        self.ffmpeg.close_pipe()
