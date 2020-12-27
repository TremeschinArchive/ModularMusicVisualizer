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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH, LOG_SEPARATOR, STEP_SEPARATOR
import numpy as np
import threading
import logging
import toml
import time
import copy
import sys
import os


class MMVSkiaCore:
    def __init__(self, mmv_main, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaCore.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_main = mmv_main
        self.prelude = self.mmv_main.prelude
        self.preludec = self.prelude["mmvcore"]

        # Log creation
        if self.preludec["log_creation"]:
            logging.info(f"{depth}{debug_prefix} Created MMVSkiaCore()")

    # Execute MMV, core loop
    def run(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaCore.run]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Executing MMVSkiaCore.run()")

        # # Save info so we can utilize on post processing or somewhere else

        last_session_info_file = self.mmv_main.mmvskia_interface.top_level_interace.last_session_info_file
        logging.info(f"{depth}{debug_prefix} Saving partial session info to last_session_info file at [{last_session_info_file}]")

        # Quit if code flow says so
        if self.prelude["flow"]["stop_at_mmv_core_run"]:
            logging.critical(f"{ndepth}{debug_prefix} Not continuing because stop_at_mmv_core_run key on prelude.toml is True")
            sys.exit(0)

        # Don't write any videos, just process the audio (useful for debugging)
        ONLY_PROCESS_AUDIO = self.prelude["flow"]["only_process_audio"]
        logging.info(f"{depth}{debug_prefix} Only process audio: [{ONLY_PROCESS_AUDIO}]")

        # Create the pipe write thread
        if not ONLY_PROCESS_AUDIO:
            logging.info(f"{depth}{debug_prefix} Creating pipe writer thread")
            self.pipe_writer_loop_thread = threading.Thread(
                target = self.mmv_main.ffmpeg.pipe_writer_loop,
                args = (self.mmv_main.audio.duration,),
                daemon = True,
            )

            # Start the thread to write images onto FFmpeg
            logging.info(f"{depth}{debug_prefix} Starting pipe writer thread")
            self.pipe_writer_loop_thread.start()

            # Init Skia
            logging.info(f"{depth}{debug_prefix} Init Skia")
            self.mmv_main.skia.init(
                width = self.mmv_main.context.width,
                height = self.mmv_main.context.height,
                render_backend = self.mmv_main.context.skia_render_backend,
            )

        # How many steps is the audio duration times the frames per second
        self.mmv_main.context.total_steps = int(self.mmv_main.audio.duration * self.mmv_main.context.fps)
        logging.info(f"{depth}{debug_prefix} Total steps: {self.mmv_main.context.total_steps}")

        # Update info that might have been changed by the user
        logging.info(f"{depth}{debug_prefix} Update Context bases")
        self.mmv_main.context.update_biases()

        # What to log and what not to
        LOG_STEP = self.preludec["run"]["log_step"]
        LOG_OFFSETTED_STEP = self.preludec["run"]["log_offsetted_step"]
        LOG_MODULATORS = self.preludec["run"]["log_modulators"]
        LOG_NEXT_STEPS = self.preludec["run"]["log_next_steps"]

        # We use audio amplitudes on MMVShaders for syncing shaders with the last rendered
        # video. Does not easily work with custom input video, you have to feed values for
        # every frame
        WRITE_AUDIO_AMPLITUDE_VALUES_TO_LAST_SESSION_INFO = \
            self.preludec["run"]["last_session_info"]["write_audio_amplitude_values"]

        # Create empty array for saving the audio amplitudes
        if WRITE_AUDIO_AMPLITUDE_VALUES_TO_LAST_SESSION_INFO:
            recorded_audio_amplitudes = []
        
        # # Last session info

        # Reset last session info file
        self.mmv_main.utils.reset_file(last_session_info_file)
        
        # Dump to toml file
        self.mmv_main.utils.dump_toml(
            data = {
                "output_video": self.mmv_main.context.output_video,
                "frame_count": self.mmv_main.context.total_steps,
                "width": self.mmv_main.context.width,
                "height": self.mmv_main.context.height,
            },
            path = last_session_info_file
        )

        # # Main routine

        logging.info(f"{depth}{debug_prefix} Start main routine")
        for step in range(0, self.mmv_main.context.total_steps):

            # Log current step, next iteration
            if LOG_STEP:
                logging.debug(STEP_SEPARATOR)
                logging.debug(f"{depth}{debug_prefix} Next step:")

            # The "raw" frame index we're at
            global_frame_index = step
            
            # # # [ Slice the audio ] # # #

            # Add the offset audio step (because interpolation isn't instant for smoothness)
            self.this_step = step + self.mmv_main.context.offset_audio_before_in_many_steps

            # If this step is out of bounds because the offset, set it to its max value
            if self.this_step >= self.mmv_main.context.total_steps - 1:
                self.this_step = self.mmv_main.context.total_steps - 1

            # Log offset step
            if LOG_OFFSETTED_STEP:
                logging.debug(f"{depth}{debug_prefix} Offsetted step by [{self.mmv_main.context.offset_audio_before_in_many_steps}] is [{self.this_step}]")

            # The current time in seconds we're going to slice the audio based on its sample rate
            # If we offset to the opposite way, the starting point can be negative hence the max function.
            current_time = max((1/self.mmv_main.context.fps) * self.this_step, 0)

            # Current time we're processing
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
                fft, frequencies = self.mmv_main.audio_processing.process(
                    data = channel_data,
                    original_sample_rate = self.mmv_main.audio.sample_rate,
                )

                # Add to the lists
                fft_list.append(fft)
                frequencies_list.append(frequencies)

            # We can access this dictionary from anyone for this step audio information
            self.modulators = {
                "average_value": self.mmv_main.audio_processing.average_value * self.mmv_main.context.audio_amplitude_multiplier,
                "fft": fft_list,
                "frequencies": frequencies_list,
            }

            # Append audio amplitude to the list
            if WRITE_AUDIO_AMPLITUDE_VALUES_TO_LAST_SESSION_INFO:
                recorded_audio_amplitudes.append(self.modulators["average_value"])
        
            # Log modulators
            if LOG_MODULATORS:
                logging.debug(f"{depth}{debug_prefix} Modulators on this step: [{self.modulators}]")

            # # # [ Next steps ] # # #

            # Don't draw anything or pipe to FFmpeg if we're only processing the audio
            if not ONLY_PROCESS_AUDIO:
                
                # Reset skia canvas
                if LOG_NEXT_STEPS:
                    logging.debug(f"{depth}{debug_prefix} Reset skia canvas")
                self.mmv_main.skia.reset_canvas()

                # Process next animation with audio info and the step count to process on
                if LOG_NEXT_STEPS:
                    logging.debug(f"{depth}{debug_prefix} Call MMVSkiaAnimation.next()")
                self.mmv_main.mmv_animation.next()

                # Next image to pipe
                if LOG_NEXT_STEPS:
                    logging.debug(f"{depth}{debug_prefix} Get next image from canvas array")
                next_image = self.mmv_main.skia.canvas_array()

                # Save current canvas's Frame to the final video, the pipe writer thread will actually pipe it
                if LOG_NEXT_STEPS:
                    logging.debug(f"{depth}{debug_prefix} Write image to FFmpeg pipe index [{global_frame_index}]")
                self.mmv_main.ffmpeg.write_to_pipe(global_frame_index, next_image)
            
            else:  # QOL print what is happening
                print(f"\rOnly process audio [{global_frame_index} / {self.mmv_main.context.total_steps}", end="")

        # End pipe, no pipe to close if we're only processing audio
        if not ONLY_PROCESS_AUDIO:
            logging.info(f"{depth}{debug_prefix} Call to close pipe, let it wait until it's done")
            self.mmv_main.ffmpeg.close_pipe()

        # Update the TOML with the new data
        if WRITE_AUDIO_AMPLITUDE_VALUES_TO_LAST_SESSION_INFO:

            # Load and change the key we're interested in
            previous_session_info_data = self.mmv_main.utils.load_toml(path = last_session_info_file)
            previous_session_info_data["audio_amplitudes"] = recorded_audio_amplitudes

            # Dump to toml file
            self.mmv_main.utils.dump_toml(
                data = previous_session_info_data,
                path = last_session_info_file,
            )
