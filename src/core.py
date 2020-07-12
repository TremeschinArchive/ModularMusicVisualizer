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
import numpy as np
import threading
import pickle
import time
import copy
import ray
import sys
import os


@ray.remote
class Worker():

    def get_canvas_multiprocess_return(self, instructions, worker_id):

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
            for item in instructions_content[index]:
                item.blit(canvas)
                del item

        # canvas.canvas.save("data/d%s.png" % instructions_index)
        canvas.resolve_pending()

        # canvas.canvas.save("data/da%s.png" % index)
        return canvas.canvas


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

        self.multiprocessed = self.context.multiprocessed

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

    def write_to_pipe_from_multiprocessing(self):
        while True:
            if self.total_steps - 1 == self.count:
                self.ffmpeg.close_pipe()
                ray.shutdown()
                break
            
            if self.count in list(self.returned_images.keys()):
                image = self.returned_images[self.count]
                self.ffmpeg.write_to_pipe(self.count, image)
                del self.returned_images[self.count]
                self.count += 1
            else:
                time.sleep(0.1)
                # print("waiting for", self.count, self.mp_return_dict.keys())

    def new_ray_process(self, global_frame_index, worker_id, update_dict):
        self.returned_images[
            global_frame_index
        ] = ray.get(
            self.ray_processes[worker_id]
            .get_canvas_multiprocess_return
            .remote(update_dict, worker_id)
        )

    def run(self):

        debug_prefix = "[Core.run]"

        # How many steps is the audio duration times the frames per second
        self.total_steps = int(self.context.duration * self.context.fps)

        print(debug_prefix, "Total steps:", self.total_steps)

        # Generate the assets
        # self.assets.pygradienter("particles", 150, 150, 20)

        # Generate a Animation
        self.mmvanimation.generate(self.canvas)

        if self.context.multiprocessed:
            ray.init(
                num_cpus=self.context.multiprocessing_workers,
            )
            self.ray_processes = {}
            self.returned_images = {}
            for index in range(self.context.multiprocessing_workers):
                self.ray_processes[index] = Worker.remote()
            self.write_thread = threading.Thread(target=self.write_to_pipe_from_multiprocessing).start()
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
            
            if self.multiprocessed:

                while global_frame_index - self.count >= self.context.multiprocessing_workers*2:
                    self.controller.core_waiting = True
                    time.sleep(0.05)
                
                self.controller.core_waiting = False

                # print("new item", global_frame_index, "asking worker", global_frame_index % self.context.multiprocessing_workers)
                
                update_dict = {
                    "content": self.mmvanimation.content,
                    "canvas": self.canvas,
                    "context": self.context,
                    "fftinfo": fftinfo,
                    "index": global_frame_index
                }

                threading.Thread(
                    target=self.new_ray_process,
                    args=(
                        global_frame_index,
                        global_frame_index % self.context.multiprocessing_workers,
                        pickle.dumps(update_dict, protocol=pickle.HIGHEST_PROTOCOL)
                    )
                ).start()
            else:
                # Save current canvas's Frame to the final video
                self.ffmpeg.write_to_pipe(global_frame_index, self.canvas.canvas)

                # Hard debug, save the canvas into a folder
                # self.canvas.canvas.save("data/canvas%s.png" % this_step)
            
            # [ FAILSAFE ] Reset the canvas (not needed if full background is present (recommended))
            if not self.context.multiprocessed:
                self.canvas.reset_canvas()
    
        if not self.context.multiprocessed:
            # We're out of animation steps, close the pipe to finish the video
            self.ffmpeg.close_pipe()
