"""
===============================================================================

Purpose: Main file to execute PyGradienter

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

from mmv.pygradienter.profiles.creepy_circles import PyGradienterProfileCreepyCircles
from mmv.pygradienter.profiles.mushy_colorful import PyGradienterProfileMushyColorful
from mmv.pygradienter.profiles.simple_smooth import PyGradienterProfileSimpleSmooth
from mmv.pygradienter.profiles.particles import PyGradienterProfileParticles
from mmv.pygradienter.profiles.simple import PyGradienterProfileSimple
from mmv.pygradienter.profiles.fabric import PyGradienterProfileFabric
from mmv.pygradienter.pyg_processing import PyGradienterProcessing
from mmv.pygradienter.pyg_worker import pyg_generate_from_profile
import multiprocessing
import threading
import pickle
import sys


class PyGradienterMain:

    def put_on_queue(self, info):
        self.put_queue.put(info)

    def generate(self, width, height, n_images, profile, quiet=False, n_workers=4):

        n_workers = min(n_images, n_workers)

        profile_and_respective_classes = {
            "creepy_circles": PyGradienterProfileCreepyCircles,
            "mushy_colorful": PyGradienterProfileMushyColorful,
            "simple_smooth": PyGradienterProfileSimpleSmooth,
            "particles": PyGradienterProfileParticles,
            "simple": PyGradienterProfileSimple,
            "fabric": PyGradienterProfileFabric,
        }

        profile = profile_and_respective_classes.get(profile, None)

        if profile == None:
            print(f"Couldn't find profile [{profile}] on keys [{list(profile_and_respective_classes.keys())}]")
            sys.exit(-1)
 
        print("Profile class", profile)

        self.put_queue = multiprocessing.Queue()
        self.get_queue = multiprocessing.Queue()

        info = {
            "process": PyGradienterProcessing(profile, width, height),
            "width": width,
            "height": height,
        }

        workers = []

        for worker_id in range(n_workers):
            workers.append(
                multiprocessing.Process(
                    target=pyg_generate_from_profile,
                    args=(
                        self.get_queue,
                        self.put_queue,
                        worker_id,
                    )
                )
            )
        
        for i, worker in enumerate(workers):
            print("Starting worker", i)
            worker.start()

        for index in range(n_images):
            print("Putting on queue index", index)
            threading.Thread(
                target=self.put_on_queue,
                args=( pickle.dumps(info, protocol=pickle.HIGHEST_PROTOCOL), )
            ).start()
        
        finished = []

        for _ in range(n_images):
            finished.append(self.get_queue.get())
        
        for worker in workers:
            worker.terminate()

        return finished
