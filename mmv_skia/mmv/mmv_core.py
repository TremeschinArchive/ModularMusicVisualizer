"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

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

import numpy as np
import threading
import time
import copy
import os


class Core:
    def __init__(self, mmv) -> None:
        self.mmv = mmv

    # Execute MMV, core loop
    def run(self) -> None:
        
        debug_prefix = "[Core.run]"

        # Create the pipe write thread
        print(debug_prefix, "Creating pipe writer thread")
        self.pipe_writer_loop_thread = threading.Thread(
            target = self.mmv.ffmpeg.pipe_writer_loop,
            args = (self.mmv.audio.duration,),
            daemon = True,
        )

        # Start the thread to write images onto FFmpeg
        print(debug_prefix, "Starting pipe writer thread")
        self.pipe_writer_loop_thread.start()
        
        # How many steps is the audio duration times the frames per second
        self.mmv.context.total_steps = int(self.mmv.audio.duration * self.mmv.context.fps)
        print(debug_prefix, "Total steps:", self.mmv.context.total_steps)

        # Init Skia
        print(debug_prefix, "Init Skia")
        self.mmv.skia.init(
            width = self.mmv.context.width,
            height = self.mmv.context.height,
            render_backend = self.mmv.context.skia_render_backend,
        )

        # Update info that might have been changed by the user
        print(debug_prefix, "Update Context bases")
        self.mmv.context.update_biases()

        # Main routine
        print(debug_prefix, "Start main routine")
        for step in range(0, self.mmv.context.total_steps):

            # The "raw" frame index we're at
            global_frame_index = step
            
            # # # [ Slice the audio ] # # #

            # Add the offset audio step (because interpolation isn't instant for smoothness)
            self.this_step = step + self.mmv.context.offset_audio_before_in_many_steps

            # If this step is out of bounds because the offset, set it to its max value
            if self.this_step >= self.mmv.context.total_steps - 1:
                self.this_step = self.mmv.context.total_steps - 1
            
            # The current time in seconds we're going to slice the audio based on its sample rate
            # If we offset to the opposite way, the starting point can be negative hence the max function.
            current_time = max((1/self.mmv.context.fps) * self.this_step, 0)

            self.mmv.context.current_time = (1/self.mmv.context.fps) * self.this_step

            # The current time in sample count to slice the audio
            this_time_in_samples = int(current_time * self.mmv.audio.sample_rate)

            # The slice starts at the this_time_in_samples and end the cut here
            until = int(this_time_in_samples + self.mmv.context.batch_size)

            # Slice the audio
            self.mmv.audio_processing.slice_audio(
                stereo_data = self.mmv.audio.stereo_data,
                mono_data = self.mmv.audio.mono_data,
                sample_rate = self.mmv.audio.sample_rate,
                start_cut = this_time_in_samples,
                end_cut = until,
                batch_size = self.mmv.context.batch_size
            )

            # # # [ Calculate the FFTs ] # # #

            fft_list = []
            frequencies_list = []

            # For each sliced channel data we have, process that into the FFTs list
            for channel_data in self.mmv.audio_processing.audio_slice:
               
                # Process this audio sample
                fft, frequencies = self.mmv.audio_processing.process(channel_data, self.mmv.audio.sample_rate)

                # Add to the lists
                fft_list.append(fft)
                frequencies_list.append(frequencies)

            # We can access this dictionary from anyone for this step audio information
            self.modulators = {
                "average_value": self.mmv.audio_processing.average_value * self.mmv.context.audio_amplitude_multiplier,
                "fft": fft_list,
                "frequencies": frequencies_list,
            }

            # # # [ Next steps ] # # #

            # Reset skia canvas
            self.mmv.skia.reset_canvas()

            # Process next animation with audio info and the step count to process on
            self.mmv.mmv_animation.next()

            # Next image to pipe
            next_image = self.mmv.skia.canvas_array()

            # Save current canvas's Frame to the final video, the pipe writer thread will actually pipe it
            self.mmv.ffmpeg.write_to_pipe(global_frame_index, next_image)

        # End pipe
        print(debug_prefix, "Call to close pipe, let it wait until it's done")
        self.mmv.ffmpeg.close_pipe()
