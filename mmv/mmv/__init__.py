"""
===============================================================================

Purpose: Main package file for MMV where the main wrapper class is located

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

from mmv.mmv_generator import MMVParticleGenerator
from mmv.mmv_visualizer import MMVVisualizer
from mmv.mmv_generator import MMVGenerator
from mmv.pygradienter import pygradienter
from mmv.common.utils import Utils
from mmv.mmv_image import MMVImage
from mmv.mmv_main import MMVMain
import time
import sys
import os


# Main wrapper class for the end user, facilitates MMV in a whole
class mmv:

    def __init__(self, watch_processing_video_realtime=False):
        # Main class of MMV
        self.main = MMVMain()

        # Utilities
        self.utils = Utils()

        # Start MMV classes that main connects them, do not run
        self.main.setup(cli=False)

        # Default options of performance and quality, 720p60
        self.performance()
        self.quality()

        # Configuring options
        self.quality_preset = QualityPreset(self)
        self.audio_processing = AudioProcessing(self)
        
        self.main.context.watch_processing_video_realtime = watch_processing_video_realtime

    def performance(self, multiprocessed=False, workers=4):
        self.main.context.multiprocessed = multiprocessed
        self.main.context.multiprocessing_workers = workers
    
    def quality(self, width=1280, height=720, fps=60):
        self.main.context.width = width
        self.main.context.height = height
        self.main.context.fps = fps
        self.width = width
        self.height = height
        self.resolution = [width, height]
    
    def input_audio(self, path):
        path = self.utils.get_abspath(path)
        if not os.path.exists(path):
            print("Input audio path does not exist [%s]" % path)
            sys.exit(-1)
        self.main.context.input_file = path
    
    def assets_dir(self, path):
        path = self.utils.get_abspath(path)
        self.utils.mkdir_dne(path)
        self.assets_dir = path
        self.main.context.assets = path
    
    def create_pygradienter_asset(self, profile, width, height, n=1, delete_existing_files=False):
        if self.main.context.os == "windows":
            print("PyGradienter only works under Linux for now :(")
            input("Press enter to continue")
        else:
            self.main.assets.pygradienter(profile, width, height, n, delete_existing_files=delete_existing_files)
    
    def output_video(self, path):
        path = self.utils.get_abspath(path)
        self.main.context.output_video = path
    
    def run(self):
        self.main.run()
    
    def image_object(self):
        return MMVImage(self.main.context)
    
    def pygradienter(self, workers=4):
        return pygradienter(workers=workers)
    
    def generator_object(self):
        return MMVGenerator(self.main.context)

    def random_file_from_dir(self, path):
        return self.utils.random_file_from_dir(path)
    
    def add(self, item, layer=0):
        if self.utils.is_matching_type([item], [MMVImage]):
            self.main.core.mmvanimation.content[layer].append(item)
        if self.utils.is_matching_type([item], [MMVGenerator]):
            self.main.core.mmvanimation.generators.append(item)
        
    def get_unique_id(self):
        return self.utils.get_hash(str(time.time()))


class QualityPreset:
    def __init__(self, mmv):
        self.mmv = mmv
    
    def sd24(self):
        self.mmv.main.context.width = 854 
        self.mmv.main.context.height = 480
        self.mmv.main.context.fps = 24
    
    def hd30(self):
        self.mmv.main.context.width = 1280 
        self.mmv.main.context.height = 720
        self.mmv.main.context.fps = 30
    
    def fullhd60(self):
        self.mmv.main.context.width = 1920 
        self.mmv.main.context.height = 1080
        self.mmv.main.context.fps = 60

    def quadhd60(self):
        self.mmv.main.context.width = 2560
        self.mmv.main.context.height = 1440
        self.mmv.main.context.fps = 60


class AudioProcessing:
    def __init__(self, mmv):
        self.mmv = mmv
    
    def preset_custom(self, config):
        self.mmv.main.audio_processing.config = config

    def preset_balanced(self):
        self.mmv.main.audio_processing.config = {
            0: {
                "sample_rate": 440,
                "get_frequencies": "range",
                "start_freq": 40,
                "end_freq": 220,
                "nbars": "original",
            },

            1: {
                "sample_rate": 4000,
                "get_frequencies": "range",
                "start_freq": 220,
                "end_freq": 2000,
                "nbars": "original", #"300,max",
            },

            2: {
                "sample_rate": 32000,
                "get_frequencies": "range",
                "start_freq": 2000,
                "end_freq": 16000,
                "nbars": "200,max",
            },
        }
    
    def preset_bass_mid(self):
        self.mmv.main.audio_processing.config = {
            0: {
                "sample_rate": 4000,
                "get_frequencies": "all",
                "start_freq": 30,
                "end_freq": 2000,
                "nbars": "original",
            },
        }
    
    