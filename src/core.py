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
import multiprocessing
import threading
import pickle
import time
import copy
import os

with open("./communicate.txt", "w") as f:
    f.write("")


def get_canvas_multiprocess_return(queue, worker_id, return_dict):

    while True:
        
        instructions = queue.get()

        start = time.time()

        if instructions == "stop":
            break
    
        canvas = instructions["canvas"]
        instructions_content = instructions["content"]
        canvas = instructions["canvas"]
        fftinfo = instructions["fftinfo"]
        instructions_index = instructions["index"]

        del instructions

        with open("./communicate.txt", "a") as f:
            f.write(str(worker_id) + " " + str(instructions_index) + " " + str(time.time() - start) + " start\n")

        canvas.reset_canvas()

        with open("./communicate.txt", "a") as f:
            f.write(str(worker_id) + " " + str(instructions_index) + " " + str(time.time() - start) + " reset canvas\n")

        for index in sorted(list(instructions_content.keys())):
            for item in instructions_content[index]:
                item.resolve_pending()
        
        with open("./communicate.txt", "a") as f:
            f.write(str(worker_id) + " " + str(instructions_index) + " " + str(time.time() - start) + " item resolve pending\n")
  
        for index in sorted(list(instructions_content.keys())):
            for item in instructions_content[index]:     
                item.blit(canvas)

        with open("./communicate.txt", "a") as f:
            f.write(str(worker_id) + " " + str(instructions_index) + " " + str(time.time() - start) + " blit\n")

        # canvas.canvas.save("data/d%s.png" % instructions_index)
        canvas.resolve_pending()

        with open("./communicate.txt", "a") as f:
            f.write(str(worker_id) + " " + str(instructions_index) + " " + str(time.time() - start) + " resolve pending canvas\n")
        # canvas.canvas.save("data/da%s.png" % index)
        # print(index, "returning")
        return_dict[instructions_index] = copy.deepcopy(canvas.canvas.image_array())


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
            print("applying async", worker_id)
            multiprocessing.Process(
            # self.pool.apply_async(
                target=get_canvas_multiprocess_return,
                # get_canvas_multiprocess_return,
                args=(
                    self.queue,
                    worker_id,
                    self.mp_return_dict
                )
            # )
            ).start()
            print("Applied async")
    
    def write_to_pipe_from_multiprocessing(self):
        while True:
            if self.total_steps - 1 == self.count:
                self.ffmpeg.close_pipe()
                for _ in range(self.context.multiprocessing_workers):
                    self.queue.put("stop")
                break
            
            for key in self.mp_return_dict.keys():
                if key < self.count:
                    del self.mp_return_dict[key]
            
            if self.count in list(self.returned_images.keys()):
                image = self.returned_images[self.count]
                self.ffmpeg.write_to_pipe(image, already_PIL_Image=True)
                del self.returned_images[self.count]
                self.count += 1
            else:
                time.sleep(0.1)
                # print("waiting for", self.count, self.mp_return_dict.keys())

    def get_mp_return_dict_to_returned_images(self, index):
        self.returned_images[index] = self.mp_return_dict[index]
        del self.mp_return_dict[index]

    def get_images_from_shared_dict(self):
        while not self.ffmpeg.stop_piping:
            for index in list(self.mp_return_dict.keys()):
                if not index in self.already_returned_image_indexes:
                    self.already_returned_image_indexes.append(index)
                    threading.Thread(
                        target=self.get_mp_return_dict_to_returned_images,
                        args=(index,)
                    ).start()


    def put_on_queue(self, update_dict):
        start = time.time()
        self.queue.put(update_dict)
        with open("./communicate.txt", "a") as f:
            f.write("run" + " " + "0" + " " + str(time.time() - start) + " put on queue\n")

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
            # ctx = multiprocessing.get_context("spawn")
            # self.pool = ctx.Pool(processes=self.context.multiprocessing_workers)
            # self.manager = ctx.Manager()
            self.pool = multiprocessing.Pool(processes=self.context.multiprocessing_workers)
            self.manager = multiprocessing.Manager()
            self.mp_return_dict = self.manager.dict()
            self.already_returned_image_indexes = []
            self.returned_images = {}
            self.queue = multiprocessing.Queue()
            self.write_thread = threading.Thread(target=self.write_to_pipe_from_multiprocessing).start()
            self.get_images_from_shared_dict = threading.Thread(target=self.get_images_from_shared_dict).start()
            self.setup_multiprocessing()
        else:
            self.canvas.reset_canvas()

        # Next animation
        for this_step in range(0, self.total_steps):
            global_frame_index = this_step
            
            start = time.time()

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

            # Get the audio slice
            audio_slice = self.audio.data[0][this_time_sample:until]

            # Calculate the fft on the frequencies
            fft = self.fourier.fft(
                audio_slice,
                self.audio.info
            )

            with open("./communicate.txt", "a") as f:
                f.write("run" + " " + str(global_frame_index) + " " + str(time.time() - start) + " ffts\n")

            # Process next animation with audio info and the step count to process on
            start = time.time()
            content = self.mmvanimation.next(audio_slice, fft, this_step)
            with open("./communicate.txt", "a") as f:
                f.write("run" + " " + str(global_frame_index) + " " + str(time.time() - start) + " next\n")

            if self.context.multiprocessed:

                while global_frame_index - self.count >= self.context.multiprocessing_workers*2:
                    # print("waiting")
                    time.sleep(0.05)

                # print("new item", global_frame_index)

                start = time.time()

                update_dict = { 
                    "content": content["content"],
                    "canvas": self.canvas,
                    "context": self.context,
                    "fftinfo": content["fftinfo"],
                    "index": global_frame_index
                }

                with open("./communicate.txt", "a") as f:
                    f.write("run" + " " + str(global_frame_index) + " " + str(time.time() - start) + " make update dict\n")

                start = time.time()

                threading.Thread(
                    target=self.put_on_queue,
                    args=(copy.deepcopy(update_dict),)
                ).start()
                
                with open("./communicate.txt", "a") as f:
                    f.write("run" + " " + str(global_frame_index) + " " + str(time.time() - start) + " deepcopy instructions\n")

            else:
                # Save current canvas's Frame to the final video
                self.ffmpeg.write_to_pipe(self.canvas.canvas)

                # Hard debug, save the canvas into a folder
                # self.canvas.canvas.save("data/canvas%s.png" % this_step)
            
            # [ FAILSAFE ] Reset the canvas (not needed if full background is present (recommended))
            if not self.context.multiprocessed:
                self.canvas.reset_canvas()
    
        if not self.context.multiprocessed:
            # We're out of animation steps, close the pipe to finish the video
            self.ffmpeg.close_pipe()
