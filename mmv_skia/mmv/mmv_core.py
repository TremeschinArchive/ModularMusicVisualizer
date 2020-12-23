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

from mmv.common.cmn_constants import NEXT_DEPTH, NO_DEPTH
import numpy as np
import threading
import logging
import time
import copy
import sys
import os


class MMVCore:
    def __init__(self, mmv_main) -> None:
        self.mmv_main = mmv_main
        self.prelude = self.mmv_main.prelude

    # Execute MMV, core loop
    def run(self, depth = NO_DEPTH) -> None:
        debug_prefix = "[MMVCore.run]"
        ndepth = depth + NEXT_DEPTH

        logging.info(f"{ndepth}{debug_prefix} Executing MMVCore.run()")

        # Quit if code flow says so
        if self.prelude["flow"]["stop_at_mmv_core_run"]:
            logging.critical(f"{ndepth}{debug_prefix} Not continuing because stop_at_mmv_core_run key on prelude.toml")
            sys.exit(0)

        # Create the pipe write thread
        logging.info(f"{ndepth}{debug_prefix} Creating pipe writer thread")
        self.pipe_writer_loop_thread = threading.Thread(
            target = self.mmv_main.ffmpeg.pipe_writer_loop,
            args = (self.mmv_main.audio.duration,),
            daemon = True,
        )

        # Start the thread to write images onto FFmpeg
        logging.info(f"{ndepth}{debug_prefix} Starting pipe writer thread")
        self.pipe_writer_loop_thread.start()
        
        # How many steps is the audio duration times the frames per second
        self.mmv_main.context.total_steps = int(self.mmv_main.audio.duration * self.mmv_main.context.fps)
        logging.info(f"{ndepth}{debug_prefix} Total steps: {self.mmv_main.context.total_steps}")

        # Init Skia
        logging.info(f"{ndepth}{debug_prefix} Init Skia")
        self.mmv_main.skia.init(
            width = self.mmv_main.context.width,
            height = self.mmv_main.context.height,
            render_backend = self.mmv_main.context.skia_render_backend,
        )

        # Update info that might have been changed by the user
        logging.info(f"{ndepth}{debug_prefix} Update Context bases")
        self.mmv_main.context.update_biases()

        # Main routine
        logging.info(f"{ndepth}{debug_prefix} Start main routine")
        for step in range(0, self.mmv_main.context.total_steps):

            # The "raw" frame index we're at
            global_frame_index = step
            
            # # # [ Slice the audio ] # # #

            # Add the offset audio step (because interpolation isn't instant for smoothness)
            self.this_step = step + self.mmv_main.context.offset_audio_before_in_many_steps

            # If this step is out of bounds because the offset, set it to its max value
            if self.this_step >= self.mmv_main.context.total_steps - 1:
                self.this_step = self.mmv_main.context.total_steps - 1
            
            # The current time in seconds we're going to slice the audio based on its sample rate
            # If we offset to the opposite way, the starting point can be negative hence the max function.
            current_time = max((1/self.mmv_main.context.fps) * self.this_step, 0)

            self.mmv_main.context.current_time = (1/self.mmv_main.context.fps) * self.this_step

            # The current time in sample count to slice the audio
            this_time_in_samples = int(current_time * self.mmv_main.audio.sample_rate)

            # The slice starts at the this_time_in_samples and end the cut here
            until = int(this_time_in_samples + self.mmv_main.context.batch_size)

            # Slice the audio
            self.mmv_main.audio_processing.slice_audio(
                stereo_data = self.mmv_main.audio.stereo_data,
                mono_data = self.mmv_main.audio.mono_data,
                sample_rate = self.mmv_main.audio.sample_rate,
                start_cut = this_time_in_samples,
                end_cut = until,
                batch_size = self.mmv_main.context.batch_size
            )

            # # # [ Calculate the FFTs ] # # #

            fft_list = []
            frequencies_list = []

            # For each sliced channel data we have, process that into the FFTs list
            for channel_data in self.mmv_main.audio_processing.audio_slice:
               
                # Process this audio sample
                fft, frequencies = self.mmv_main.audio_processing.process(channel_data, self.mmv_main.audio.sample_rate)

                # Add to the lists
                fft_list.append(fft)
                frequencies_list.append(frequencies)

            # We can access this dictionary from anyone for this step audio information
            self.modulators = {
                "average_value": self.mmv_main.audio_processing.average_value * self.mmv_main.context.audio_amplitude_multiplier,
                "fft": fft_list,
                "frequencies": frequencies_list,
            }

            # # # [ Next steps ] # # #

            # Reset skia canvas
            self.mmv_main.skia.reset_canvas()

            # Process next animation with audio info and the step count to process on
            self.mmv_main.mmv_animation.next()

            # Next image to pipe
            next_image = self.mmv_main.skia.canvas_array()

            # Save current canvas's Frame to the final video, the pipe writer thread will actually pipe it
            self.mmv_main.ffmpeg.write_to_pipe(global_frame_index, next_image)

        # End pipe
        logging.info(f"{ndepth}{debug_prefix} Call to close pipe, let it wait until it's done")
        self.mmv_main.ffmpeg.close_pipe()
