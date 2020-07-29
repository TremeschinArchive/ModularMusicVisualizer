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
from mmv.common.cmn_utils import Utils
from mmv.mmv_image import MMVImage
from mmv.mmv_main import MMVMain
import uuid
import time
import sys
import os


# Main wrapper class for the end user, facilitates MMV in a whole
class mmv:

    # Start default configs, creates wrapper classes
    def __init__(self, watch_processing_video_realtime: bool=False) -> None:

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
        self.audio_processing = AudioProcessingPresets(self)
        self.post_processing = self.main.canvas.configure

        # Has the user chosen to watch the processing video realtime?
        self.main.context.watch_processing_video_realtime = watch_processing_video_realtime

    # Execute MMV with the configurations we've done
    def run(self) -> None:
        self.main.run()

    # Performance settings, if we'll be running linearly or with N MMV Workers
    def performance(self, multiprocessed: bool=False, workers: int=4) -> None:
        self.main.context.multiprocessed = multiprocessed
        self.main.context.multiprocessing_workers = workers
    
    # Define output video width, height and frames per second
    def quality(self, width: int=1280, height: int=720, fps: int=60) -> None:
        self.main.context.width = width
        self.main.context.height = height
        self.main.context.fps = fps
        self.width = width
        self.height = height
        self.resolution = [width, height]
        self.main.canvas.create_canvas()
    
    # Set the input audio file, raise exception if it does not exist
    def input_audio(self, path: str) -> None:
        path = self.utils.get_abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError("Input audio path does not exist [%s]" % path)
        self.main.context.input_file = path
    
    # Output path where we'll be saving the final video
    def output_video(self, path: str) -> None:
        path = self.utils.get_abspath(path)
        self.main.context.output_video = path

    # Set the assets dir
    def assets_dir(self, path: str) -> None:
        # Remove the last "/"", pathing intuition under MMV scripts gets easier
        if path.endswith("/"):
            path = path[:-1]
        path = self.utils.get_abspath(path)
        self.utils.mkdir_dne(path)
        self.assets_dir = path
        self.main.context.assets = path
    
    # # [ MMV Objects ] # #
    
    # Add a given object to MMVAnimation content on a given layer
    def add(self, item, layer: int=0) -> None:

        # Make layers until this given layer if they don't exist
        self.main.core.mmvanimation.mklayers_until(layer)

        # Check the type and add accordingly
        if self.utils.is_matching_type([item], [MMVImage]):
            self.main.core.mmvanimation.content[layer].append(item)
            
        if self.utils.is_matching_type([item], [MMVGenerator]):
            self.main.core.mmvanimation.generators.append(item)

    # Get a blank MMVImage object
    def image_object(self) -> None:
        return MMVImage(self.main.context)
    
    # Get a pygradienter object with many workers for rendering
    def pygradienter(self, workers=4):
        return pygradienter(workers=workers)
    
    # Get a blank MMVGenerator object
    def generator_object(self):
        return MMVGenerator(self.main.context)

    # # [ Utilities ] # #

    def random_file_from_dir(self, path):
        return self.utils.random_file_from_dir(path)
        
    def get_unique_id(self):
        return self.utils.get_hash(str(uuid.uuid4()))


# Presets on width and height
class QualityPreset:

    # Get this file main mmv class
    def __init__(self, mmv) -> None:
        self.mmv = mmv
    
    # Standard definition, 480p @ 24 fps
    def sd24(self) -> None:
        self.mmv.main.context.width = 854 
        self.mmv.main.context.height = 480
        self.mmv.main.context.fps = 24
    
    # (old) HD definition, 720p @ 30 fps
    def hd30(self) -> None:
        self.mmv.main.context.width = 1280 
        self.mmv.main.context.height = 720
        self.mmv.main.context.fps = 30
    
    # Full HD definition, 1080p @ 60 fps
    def fullhd60(self) -> None:
        self.mmv.main.context.width = 1920 
        self.mmv.main.context.height = 1080
        self.mmv.main.context.fps = 60

    # Quad HD (4x720p) definition, 1440p @ 60 fps
    def quadhd60(self) -> None:
        self.mmv.main.context.width = 2560
        self.mmv.main.context.height = 1440
        self.mmv.main.context.fps = 60


# Presets on the audio processing, like how and where to apply FFTs, frequencies we want
class AudioProcessingPresets:

    # Get this file main mmv class
    def __init__(self, mmv: mmv) -> None:
        self.mmv = mmv
    
    # Custom preset, sends directly those dictionaries
    def preset_custom(self, config: dict) -> None:
        self.mmv.main.audio_processing.config = config

    # A balanced preset between the bass, mid and high frequencies
    # Good for general type of music
    def preset_balanced(self) -> None:
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
                "nbars": "fixed,200,max",
            },
        }
    
    # Get some bazz, som' mid freq
    # Good for heavy low frequencies music
    def preset_bass_mid(self) -> None:
        self.mmv.main.audio_processing.config = {
            0: {
                "sample_rate": 4000,
                "get_frequencies": "range",
                "start_freq": 60,
                "end_freq": 2000,
                "nbars": "original",
            },
        }
    