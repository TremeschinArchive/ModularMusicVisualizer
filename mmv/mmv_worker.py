"""
===============================================================================

Purpose: Worker method for MMV multiprocessing, reads instructions from a 
get_queue and writes the final frame on put_queue

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

import setproctitle
import pickle
import gc


def get_canvas_multiprocess_return(get_queue, put_queue, worker_id):
    
    # Set process name so we know who's what on a task manager
    setproctitle.setproctitle(f"MMV Worker {worker_id+1}")

    while True:

        # Unpickle our instructions        
        instructions = pickle.loads(get_queue.get())

        # Get instructions intuitive variable name
        canvas = instructions["canvas"]
        content = instructions["content"]
        fftinfo = instructions["fftinfo"]
        this_frame_index = instructions["index"]

        # Empty the canvas
        canvas.reset_canvas()

        # Resole pending operations and blit item on canvas
        for layer in sorted(content):
            [item.resolve_pending() for item in content[layer]]
        
        for layer in sorted(content):
            [item.blit(canvas) for item in content[layer]]

        # Resolve pending operations (post process mostly)
        canvas.resolve_pending()

        # Send the numpy array in RGB format back to the Core class for sending to FFmpeg
        put_queue.put( [this_frame_index, canvas.canvas.get_rgb_frame_array()] )

        # Memory management
        del instructions
        del canvas
        del content
        del fftinfo
        del this_frame_index

        gc.collect() # <-- This took 3 hours of headache with memory leaks
