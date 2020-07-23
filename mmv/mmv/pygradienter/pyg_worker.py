"""
===============================================================================

Purpose: Worker method for generating a PyGradienter profile

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

from PIL import Image
import setproctitle
import pickle


def pyg_generate_from_profile(put_queue, get_queue, worker_id):

    # Set process name so we know who's what on a task manager
    setproctitle.setproctitle(f"PyGradienter Worker {worker_id+1}")

    count = 0

    while True:

        # Unpickle our instructions        
        instructions = pickle.loads(get_queue.get())

        process = instructions["process"]
        width = instructions["width"]
        height = instructions["height"]

        process.generate(f"Worker {worker_id} - Image {count}")

        count += 1

        put_queue.put(Image.fromarray(process.canvas))
