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
        self.fourier = fourier
        self.ffmpeg = ffmpeg
        self.audio = audio
        self.mmvanimation = mmvanimation
        self.audio_processing = audio_processing

        # Utils and ROOT dir
        self.utils = Utils()
        self.ROOT = self.context.ROOT

    # Create MMV Workers with Queues from here
    def setup_multiprocessing(self) -> None:

        debug_prefix = "[Core.setup_multiprocessing]"

        # The worker objects
        self.workers = []

        # Create many workers
        for worker_id in range(self.context.multiprocessing_workers):
            
            print(debug_prefix, "Creating worker with id [%s]" % worker_id)
            
            # Create Process with inverted queues as there we..
            # "put what we get here and get what we put after"
            worker = multiprocessing.Process(
                target=get_canvas_multiprocess_return,
                args=(
                    self.core_put_queue,
                    self.core_get_queue,
                    worker_id
                ),
                # When main Python process finishes, terminate all workers
                daemon=True
            )
            worker.name = f"MMV Worker {worker_id + 1}"

            # Add the worker to the list
            self.workers.append(worker)

            print(debug_prefix, "Created new worker")

        # Wake up every worker
        for worker in self.workers:
            worker.start()

    # Keep getting items from the queue
    def core_get_queue_loop(self) -> None:
        while True:
            # Get queue returns [index, image]
            get = self.core_get_queue.get()
            index = get[0]
            image = get[1]
            self.ffmpeg.write_to_pipe(index, image)

    # Function for using threading to put dictionaries on the Queue
    def put_on_core_queue(self, update: dict) -> None:
        self.core_put_queue.put(update)
    
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

        # Setup multiprocessing queues
        if self.context.multiprocessed:
            self.returned_images = {}
            queuesize = self.context.multiprocessing_workers*2
            self.core_put_queue = multiprocessing.Queue(maxsize=queuesize)
            self.core_get_queue = multiprocessing.Queue(maxsize=queuesize)
            self.setup_multiprocessing()
            self.controller.threads["core_get_queue_loop"] = threading.Thread(target=self.core_get_queue_loop, daemon=True).start()

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

            # Process next animation with audio info and the step count to process on
            self.mmvanimation.next(fftinfo, this_step)
         
            # Multiprocessing we have to send the info to the queues for the workers to get
            if self.context.multiprocessed:

                # Update our Core loop status, are we "awaiting" for the workers to send more images?
                while global_frame_index - self.ffmpeg.count >= self.context.multiprocessing_workers * 2:
                    self.controller.core_waiting = True
                    time.sleep(0.05)
                self.controller.core_waiting = False

                # The update dictionary
                update_dict = {
                    "content": self.mmvanimation.content,
                    "canvas": self.canvas,
                    "context": self.context,
                    "fftinfo": fftinfo,
                    "index": global_frame_index
                }

                # # Yes threading is expensive, might leave this code here to test in the future 
                # threading.Thread(
                #     target=self.put_on_core_queue,
                #     args=( pickle.dumps(update_dict, protocol=pickle.HIGHEST_PROTOCOL), )
                # ).start()

                self.core_put_queue.put(pickle.dumps(update_dict, protocol=pickle.HIGHEST_PROTOCOL))

                del update_dict
                
            else:
                # Save current canvas's Frame to the final video
                self.ffmpeg.write_to_pipe(global_frame_index, self.canvas.image.image)

                # Hard debug, save the canvas into a folder
                # self.canvas.canvas.save("data/canvas%s.png" % this_step)
            
            # [ FAILSAFE ] Reset the canvas (not needed if full background is present (recommended))
            if not self.context.multiprocessed:
                self.canvas.reset_canvas()
    
        if not self.context.multiprocessed:
            # We're out of animation steps, close the pipe to finish the video
            self.ffmpeg.close_pipe()
