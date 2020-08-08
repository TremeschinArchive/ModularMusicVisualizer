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

from mmv.mmv_worker import get_canvas_multiprocess_return
from mmv.common.cmn_audio import AudioProcessing
from mmv.common.cmn_video import FFmpegWrapper
from mmv.common.cmn_skia import SkiaWrapper
from mmv.common.cmn_fourier import Fourier
from mmv.common.cmn_audio import AudioFile
from mmv.mmv_animation import MMVAnimation
from mmv.mmv_controller import Controller
from mmv.common.cmn_utils import Utils
from mmv.mmv_context import Context
from mmv.mmv_image import MMVImage
from mmv.common.cmn_types import *
import multiprocessing
import setproctitle
import numpy as np
import threading
import pickle
import time
import copy
import os
import gc


class Core:
    def __init__(self, 
            context: Context,
            controller: Controller,
            canvas: MMVImage,
            skia: SkiaWrapper,
            fourier: Fourier,
            ffmpeg: FFmpegWrapper,
            audio: AudioFile,
            mmvanimation: MMVAnimation,
            audio_processing: AudioProcessing
        ) -> None:

        # Get every class
        self.context = context
        self.controller = controller
        self.canvas = canvas
        self.skia = skia
        self.fourier = fourier
        self.ffmpeg = ffmpeg
        self.audio = audio
        self.mmvanimation = mmvanimation
        self.audio_processing = audio_processing

        # Utils and ROOT dir
        self.utils = Utils()
        self.ROOT = self.context.ROOT

    # Execute MMV, core loop
    def run(self) -> None:
        
        debug_prefix = "[Core.run]"

        # Create the pipe write thread
        self.pipe_writer_loop_thread = threading.Thread(
            target=self.ffmpeg.pipe_writer_loop,
            args=(self.audio.duration,)
        ).start()
        
        # How many steps is the audio duration times the frames per second
        self.total_steps = int(self.audio.duration * self.context.fps)
        self.controller.total_steps = self.total_steps

        print(debug_prefix, "Total steps:", self.total_steps)

        # Init skia
        self.skia.init()

        # Next animation
        for this_step in range(0, self.total_steps):

            # The "raw" frame index we're at
            global_frame_index = this_step
            
            # # # [ Slice the audio ] # # #

            # Add the offset audio step (because interpolation isn't instant for smoothness)
            this_step += self.context.offset_audio_before_in_many_steps

            # If this step is out of bounds because the offset, set it to its max value
            if this_step >= self.total_steps - 1:
                this_step = self.total_steps - 1
            
            # The current time in seconds we're going to slice the audio based on its samplerate
            # If we offset to the opposite way, the starting point can be negative hence the max function.
            time_in_seconds = max( (1/self.context.fps) * this_step, 0 )

            # The current time in sample count to slice the audio
            this_time_in_samples = int(time_in_seconds * self.audio.sample_rate)

            # The slice starts at the this_time_in_samples and end the cut here
            until = int(this_time_in_samples + self.context.batch_size)

            # Slice the audio
            self.audio_processing.slice_audio(
                stereo_data = self.audio.stereo_data,
                mono_data = self.audio.mono_data,
                sample_rate = self.audio.sample_rate,
                start_cut = this_time_in_samples,
                end_cut = until,
                batch_size = self.context.batch_size
            )

            # # # [ Calculate the FFTs ] # # #

            # The fftinfo, or call it "current time audio info", couldn't think a better var name
            fftinfo = {
                "average_value": self.audio_processing.average_value,
                "fft": [
                    # For each sliced channel data we have, process that into the FFTs list
                    self.audio_processing.process(channel_data, self.audio.sample_rate)
                    for channel_data in self.audio_processing.audio_slice
                ]
            }

            # # # [ Next steps ] # # #

            # Reset skia canvas
            self.skia.reset_canvas()

            # Process next animation with audio info and the step count to process on
            self.mmvanimation.next(fftinfo, this_step)

            # Next image to pipe
            next_image = self.skia.canvas_array()

            # Save current canvas's Frame to the final video
            self.ffmpeg.write_to_pipe(global_frame_index, next_image)

            # [ FAILSAFE ] Reset the canvas (not needed if full background is present (recommended))
            if not self.context.multiprocessed:
                self.canvas.reset_canvas()
    
        if not self.context.multiprocessed:
            # We're out of animation steps, close the pipe to finish the video
            self.ffmpeg.close_pipe()
