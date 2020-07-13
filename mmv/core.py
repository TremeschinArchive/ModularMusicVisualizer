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

from mmv.utils import Utils
import multiprocessing
import numpy as np
import threading
import pickle
import time
import copy
import os


def get_canvas_multiprocess_return(get_queue, put_queue, worker_id):

    while True:
        
        instructions = get_queue.get()

        if instructions == "stop":
            break

        instructions = pickle.loads(instructions)
    
        canvas = instructions["canvas"]
        instructions_content = instructions["content"]
        fftinfo = instructions["fftinfo"]
        instructions_index = instructions["index"]

        del instructions

        canvas.reset_canvas()

        for index in sorted(list(instructions_content.keys())):
            for item in instructions_content[index]:
                item.resolve_pending()

        for index in sorted(list(instructions_content.keys())):
            for position, item in enumerate(instructions_content[index]):
                item.blit(canvas)
                del instructions_content[index][position]

        canvas.resolve_pending()

        put_queue.put( [instructions_index, canvas.canvas.get_rgb_frame_array()] )

        del canvas
        del instructions_content
        del fftinfo
        del instructions_index


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
        self.count = 0

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
    
    def setup_multiprocessing(self):
        debug_prefix = "[Core.setup_multiprocessing]"

        for worker_id in range(self.context.multiprocessing_workers):
            print("Create worker with id [%s]" % worker_id)
            self.get_queues[worker_id] = multiprocessing.Queue()
            multiprocessing.Process(
            # self.pool.apply_async(
                target=get_canvas_multiprocess_return,
                # get_canvas_multiprocess_return,
                args=(
                    self.core_put_queue,
                    self.get_queues[worker_id],
                    worker_id
                ),
                daemon=True
            # )
            ).start()
            print("Created new worker")
    
    def write_to_pipe_from_multiprocessing(self):
        empty = [None, None]
        while True:
            if self.total_steps - 1 == self.count:
                self.ffmpeg.close_pipe()
                for _ in range(self.context.multiprocessing_workers):
                    self.queue.put("stop")
                break
            
            image = self.returned_images.pop(self.count, empty)

            if not image == empty:
                self.ffmpeg.write_to_pipe(
                    self.count,
                    image
                )
                del image
                self.count += 1
            else:
                time.sleep(0.1)
                print("waiting for", self.count)

    def get_queue_to_return_images(self, queue_index):
        while not self.ffmpeg.stop_piping:
            get = self.get_queues[queue_index].get()
            index = get[0]
            image = get[1]
            self.returned_images[index] = image
            del get
            del image
            del index

    def get_queues_loop(self):
        for queue_index in range(self.context.multiprocessing_workers):
            threading.Thread(
                target=self.get_queue_to_return_images,
                args=(queue_index,)
            ).start()

    def put_on_core_queue(self, update_dict):
        self.core_put_queue.put(update_dict)
        del update_dict
        
    def run(self):

        debug_prefix = "[Core.run]"

        # How many steps is the audio duration times the frames per second
        self.total_steps = int(self.context.duration * self.context.fps)

        print(debug_prefix, "Total steps:", self.total_steps)

        # Generate the assets
        # self.assets.pygradienter("particles", 150, 150, 20)

        if self.context.multiprocessed:
            # ctx = multiprocessing.get_context("spawn")
            # self.pool = ctx.Pool(processes=self.context.multiprocessing_workers)
            # self.manager = ctx.Manager()
            # self.pool = multiprocessing.Pool(processes=self.context.multiprocessing_workers)
            # self.mp_return_dict = self.manager.dict()
            self.manager = multiprocessing.Manager()
            self.already_returned_image_indexes = []
            self.returned_images = {}
            self.core_put_queue = multiprocessing.Queue()
            self.get_queues = {}
            self.write_thread = threading.Thread(target=self.write_to_pipe_from_multiprocessing).start()
            self.setup_multiprocessing()
            self.get_queues_loop = self.get_queues_loop()
        else:
            self.canvas.reset_canvas()

        # Next animation
        for this_step in range(0, self.total_steps):

            global_frame_index = this_step
            
            # Add the offset audio step (because interpolation isn't instant for smoothness)
            this_step += self.context.offset_audio_before_in_many_steps

            # If this step is out of bounds because the offset, set it to its max value
            if this_step >= self.total_steps - 1:
                this_step = self.total_steps - 1

            # The current time in seconds we're going to slice the audio based on its samplerate
            # If we offset to the opposite way, the starting point can be negative hence the max function.
            this_time = max( (1/self.context.fps) * this_step, 0 )

            # The current time in sample count to slice the audio
            this_time_sample = int(this_time * self.audio.info["sample_rate"])

            # The slice starts at the this_time_sample and end the cut here
            until = int(this_time_sample + self.context.batch_size)

            # Get the audio slices of the left and right channel
            audio_slice = [
                self.audio.data[0][this_time_sample:until],
                self.audio.data[1][this_time_sample:until],
            ]

            fft_audio_slice = []

            # Normalize the audio slice to 1
            for i, array in enumerate(audio_slice):
                normalize = np.linalg.norm(array)
                if not normalize == 0:
                    fft_audio_slice.append((array / normalize)*(2**(self.audio.info["bit_depth"] + 1)))
                else:
                    fft_audio_slice.append(array)

            # Calculate the FFT on the left and right channel
            fft = [
                self.fourier.fft(
                    fft_audio_slice[0],
                    self.audio.info
                ),
                self.fourier.fft(
                    fft_audio_slice[1],
                    self.audio.info
                )
            ]

            # Adapt the FFT
            mean_fft = (fft[0] + fft[1])/2
            mean_audio_slice = (audio_slice[0] + audio_slice[1]) / 2

            # Adapt the FFT
            biased_total_size = abs(sum(mean_fft)) / self.context.batch_size
            average_value = sum([abs(x)/(2**self.audio.info["bit_depth"]) for x in mean_audio_slice]) / len(mean_audio_slice)

            fftinfo = {
                "average_value": average_value,
                "biased_total_size": biased_total_size,
                "fft": fft
            }

            # Process next animation with audio info and the step count to process on
            self.mmvanimation.next(audio_slice, fftinfo, this_step)
         
            if self.context.multiprocessed:

                while global_frame_index - self.count >= self.context.multiprocessing_workers*2:
                    self.controller.core_waiting = True
                    time.sleep(0.05)
                
                self.controller.core_waiting = False

                update_dict = {
                    "content": self.mmvanimation.content,
                    "canvas": self.canvas,
                    "context": self.context,
                    "fftinfo": fftinfo,
                    "index": global_frame_index
                }
                
                threading.Thread(
                    target=self.put_on_core_queue,
                    args=(pickle.dumps(update_dict, protocol=pickle.HIGHEST_PROTOCOL),)
                ).start()

                del update_dict
                
            else:
                # Save current canvas's Frame to the final video
                self.ffmpeg.write_to_pipe(self.canvas.canvas.get_rgb_frame_array())

                # Hard debug, save the canvas into a folder
                # self.canvas.canvas.save("data/canvas%s.png" % this_step)
            
            # [ FAILSAFE ] Reset the canvas (not needed if full background is present (recommended))
            if not self.context.multiprocessed:
                self.canvas.reset_canvas()
    
        if not self.context.multiprocessed:
            # We're out of animation steps, close the pipe to finish the video
            self.ffmpeg.close_pipe()
