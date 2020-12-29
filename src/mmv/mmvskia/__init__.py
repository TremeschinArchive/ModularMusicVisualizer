"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Main package file for MMVSkia where the main wrapper class is located

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

print("[mmvskia.__init__.py package] Importing MMV package files, this might take a while from time to time..")

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, PACKAGE_DEPTH, LOG_NO_DEPTH, LOG_SEPARATOR, STEP_SEPARATOR
from mmv.mmvskia.pygradienter.pyg_main import PyGradienter
from mmv.mmvskia.mmv_generator import MMVSkiaGenerator
from mmv.mmvskia.mmv_image import MMVSkiaImage
print("[mmvskia.__init__.py package] Importing probably heaviest dependency [MMVSkiaMain], Skia might take a bit to load so does numpy, opencv etc..")
from mmv.mmvskia.mmv_main import MMVSkiaMain
from mmv.common.cmn_midi import MidiFile
from mmv.common.cmn_utils import Utils
import subprocess
import tempfile
import logging
import shutil
import math
import uuid
import time
import toml
import sys
import os


# Main wrapper class for the end user, facilitates MMV in a whole
class MMVSkiaInterface:

    # This top level interface is the "global package manager" for every subproject / subimplementation of
    # MMV, it is the class that will deal with stuff not directly related to functionality of this class 
    # and package here, mainly dealing with external deps, micro managing stuff, setting up logging,
    # loading "prelude" configurations, that is, defining behavior, not configs related to this package
    # and functionality.
    #
    # We create a MMV{Skia,Shader}Main class and we send this interface to it, and we send that instance
    # of MMV*Main to every other sub class so if we access self.mmv_main.mmvskia_interface we are accessing this
    # file here, MMVSkiaInterface, and we can quickly refer to the most top level package by doing
    # self.mmv_main.mmvskia_interface.top_level_interface, since this interface here is just the MMVSkia 
    # interface for the mmvskia package while the top level one manages both MMVSkia and MMVShader
    #
    def __init__(self, top_level_interace, depth = LOG_NO_DEPTH, **kwargs):
        debug_prefix = "[MMVSkiaInterface.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.top_level_interace = top_level_interace
        self.os = self.top_level_interace.os

        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_main.mmvskia_interface.MMV_SKIA_ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.MMV_SKIA_ROOT = os.path.dirname(os.path.abspath(__file__))
            logging.info(f"{depth}{debug_prefix} Running directly from source code")
            logging.info(f"{depth}{debug_prefix} Modular Music Visualizer Python package [__init__.py] located at [{self.MMV_SKIA_ROOT}]")
        else:
            self.MMV_SKIA_ROOT = os.path.dirname(os.path.abspath(sys.executable))
            logging.info(f"{depth}{debug_prefix} Running from release (sys.executable..?)")
            logging.info(f"{depth}{debug_prefix} Modular Music Visualizer executable located at [{self.MMV_SKIA_ROOT}]")

        # # Prelude configuration

        prelude_file = f"{self.MMV_SKIA_ROOT}{os.path.sep}mmv_skia_prelude.toml"
        logging.info(f"{depth}{debug_prefix} Attempting to load prelude file located at [{prelude_file}], we cannot continue if this is wrong..")

        with open(prelude_file, "r") as f:
            self.prelude = toml.loads(f.read())

        # Log prelude configuration
        logging.info(f"{depth}{debug_prefix} Prelude configuration is: {self.prelude}")

        # # # Create MMV classes and stuff

        # Main class of MMV and tart MMV classes that main connects them, do not run
        self.mmv_main = MMVSkiaMain(interface = self)
        self.mmv_main.setup(depth = ndepth)

        # Utilities
        self.utils = Utils()

        # Configuring options
        self.audio_processing = AudioProcessingPresets(self)
        self.post_processing = self.mmv_main.canvas.configure

        # Log a separator to mark the end of the __init__ phase
        logging.info(f"{depth}{debug_prefix} Initialize phase done!")
        logging.info(LOG_SEPARATOR)

        self.configure_mmv_main()

        # Quit if code flow says so
        if self.prelude["flow"]["stop_at_interface_init"]:
            logging.critical(f"{ndepth}{debug_prefix} Not continuing because stop_at_interface_init key on prelude.toml is True")
            sys.exit(0)

    # Read the function body for more info
    def configure_mmv_main(self, **kwargs):

        # Has the user chosen to watch the processing video realtime?
        self.mmv_main.context.audio_amplitude_multiplier = kwargs.get("audio_amplitude_multiplier", 1)
        self.mmv_main.context.skia_render_backend = kwargs.get("render_backend", "gpu")

        # # Encoding options

        # FFmpeg
        self.mmv_main.context.ffmpeg_pixel_format = kwargs.get("ffmpeg_pixel_format", "auto")
        self.mmv_main.context.ffmpeg_dumb_player = kwargs.get("ffmpeg_dumb_player", "auto")
        self.mmv_main.context.ffmpeg_hwaccel = kwargs.get("ffmpeg_hwaccel", "auto")

        # x264 specific
        self.mmv_main.context.x264_use_opencl = kwargs.get("x264_use_opencl", False)
        self.mmv_main.context.x264_preset = kwargs.get("x264_preset", "slow")
        self.mmv_main.context.x264_tune = kwargs.get("x264_tune", "film")
        self.mmv_main.context.x264_crf = kwargs.get("x264_crf", "17")

        # Pipe writer
        self.mmv_main.context.max_images_on_pipe_buffer = kwargs.get("max_images_on_pipe_buffer", 20)

    # Execute MMV with the configurations we've done
    def run(self, depth = PACKAGE_DEPTH) -> None:
        debug_prefix = "[MMVSkiaInterface.run]"
        ndepth = depth + LOG_NEXT_DEPTH
        logging.info(LOG_SEPARATOR)

        # Log action
        logging.info(f"{depth}{debug_prefix} Configuration phase done, executing MMVSkiaMain.run()..")

        # Run configured mmv_main class
        self.mmv_main.run(depth = ndepth)

    # Define output video width, height and frames per second, defaults to 720p60
    def quality(self, width: int = 1280, height: int = 720, fps: int = 60, batch_size = 2048, depth = PACKAGE_DEPTH) -> None:
        debug_prefix = "[MMVSkiaInterface.quality]"
        ndepth = depth + LOG_NEXT_DEPTH
        
        logging.info(f"{depth}{debug_prefix} Setting width={width} height={height} fps={fps} batch_size={batch_size}")
        
        # Assign values
        self.mmv_main.context.width = width
        self.mmv_main.context.height = height
        self.mmv_main.context.fps = fps
        self.mmv_main.context.batch_size = batch_size
        self.width = width
        self.height = height
        self.resolution = [width, height]

        # Create or reset a mmv canvas with that target resolution
        logging.info(f"{depth}{debug_prefix} Creating / resetting canvas with that width and height")
        self.mmv_main.canvas.create_canvas(depth = ndepth)
        logging.info(STEP_SEPARATOR)

    # Set the input audio file, raise exception if it does not exist
    def input_audio(self, path: str, depth = PACKAGE_DEPTH) -> None:
        debug_prefix = "[MMVSkiaInterface.input_audio]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action, do action
        logging.info(f"{depth}{debug_prefix} Set audio file path: [{path}], getting absolute path..")
        self.mmv_main.context.input_audio_file = self.get_absolute_path(path, depth = ndepth)
        logging.info(STEP_SEPARATOR)
    
    # Set the input audio file, raise exception if it does not exist
    def input_midi(self, path: str, depth = PACKAGE_DEPTH) -> None:
        debug_prefix = "[MMVSkiaInterface.input_midi]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action, do action
        logging.info(f"{depth}{debug_prefix} Set MIDI file path: [{path}], getting absolute path..")
        self.mmv_main.context.input_midi = self.get_absolute_path(path, depth = ndepth)
        logging.info(STEP_SEPARATOR)
    
    # Output path where we'll be saving the final video
    def output_video(self, path: str, depth = PACKAGE_DEPTH) -> None:
        debug_prefix = "[MMVSkiaInterface.output_video]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action, do action
        logging.info(f"{depth}{debug_prefix} Set output video path: [{path}], getting absolute path..")
        self.mmv_main.context.output_video = self.utils.get_abspath(path, depth = ndepth)
        logging.info(STEP_SEPARATOR)
    
    # Offset where we cut the audio for processing, mainly for interpolation latency compensation
    def offset_audio_steps(self, steps: int = 0, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVSkiaInterface.offset_audio_steps]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action, do action
        logging.info(f"{depth}{debug_prefix} Offset audio in N steps: [{steps}]")
        self.mmv_main.context.offset_audio_before_in_many_steps = steps
        logging.info(STEP_SEPARATOR)
    
    # # [ MMV Objects ] # #
    
    # Add a given object to MMVSkiaAnimation content on a given layer
    def add(self, item, layer: int = 0, depth = PACKAGE_DEPTH) -> None:
        debug_prefix = "[MMVSkiaInterface.add]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Make layers until this given layer if they don't exist
        logging.info(f"{depth}{debug_prefix} Making animations layer until N = [{layer}]")
        self.mmv_main.mmv_animation.mklayers_until(layer, depth = ndepth)

        # Check the type and add accordingly
        if self.utils.is_matching_type([item], [MMVSkiaImage]):
            logging.info(f"{depth}{debug_prefix} Add MMVSkiaImage object [{item}]")
            self.mmv_main.mmv_animation.content[layer].append(item)
            
        if self.utils.is_matching_type([item], [MMVSkiaGenerator]):
            logging.info(f"{depth}{debug_prefix} Add MMVSkiaGenerator object [{item}]")
            self.mmv_main.mmv_animation.generators.append(item)

        logging.info(STEP_SEPARATOR)

    # Get a blank MMVSkiaImage object with the first animation layer build up
    def image_object(self, depth = PACKAGE_DEPTH) -> MMVSkiaImage:
        debug_prefix = "[MMVSkiaInterface.image_object]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Creating blank MMVSkiaImage object and initializing first animation layer, returning it afterwards")
        
        # Create blank MMVSkiaImage, init the animation layers for the user
        mmv_image_object = MMVSkiaImage(self.mmv_main, depth = ndepth)
        mmv_image_object.configure.init_animation_layer(depth = ndepth)

        # Return a pointer to the object
        logging.info(STEP_SEPARATOR)
        return mmv_image_object

    # Get a blank MMVSkiaGenerator object
    def generator_object(self, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVSkiaInterface.generator_object]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Creating blank MMVSkiaGenerator object, returning it afterwards")

        # Create blank MMVSkiaGenerator, return a pointer to the object
        logging.info(STEP_SEPARATOR)
        return MMVSkiaGenerator(self.mmv_main, depth = ndepth)

    # # [ Utilities ] # #

    # Random file from a given path directory (loading random backgrounds etc)
    def random_file_from_dir(self, path, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVSkiaInterface.random_file_from_dir]"
        ndepth = depth + LOG_NEXT_DEPTH

        logging.info(f"{depth}{debug_prefix} Get absolute path and returning random file from directory: [{path}]")

        logging.info(STEP_SEPARATOR)
        return self.utils.random_file_from_dir(self.utils.get_abspath(path, depth = ndepth), depth = ndepth)

    # Make the directory if it doesn't exist
    def make_directory_if_doesnt_exist(self, path: str, depth = PACKAGE_DEPTH, silent = True) -> None:
        debug_prefix = "[MMVSkiaInterface.make_directory_if_doesnt_exist]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Make directory if doesn't exist [{path}], get absolute realpath and mkdir_dne")

        # Get absolute and realpath, make directory if doens't exist (do the action)
        path = self.utils.get_abspath(path, depth = ndepth, silent = silent)
        self.utils.mkdir_dne(path, depth = ndepth)
        logging.info(STEP_SEPARATOR)
    
    # Make the directory if it doesn't exist
    def delete_directory(self, path: str, depth = PACKAGE_DEPTH, silent = False) -> None:
        debug_prefix = "[MMVSkiaInterface.delete_directory]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Delete directory [{path}], get absolute realpath and rmdir")

        # Get absolute and realpath, delete directory (do the action)
        path = self.utils.get_abspath(path, depth = ndepth, silent = silent)
        self.utils.rmdir(path, depth = ndepth)
        logging.info(STEP_SEPARATOR)

    # Get the absolute path to a file or directory, absolute starts with / on *nix and LETTER:// on Windows
    # we expect it to exist so we quit if don't since this is the interface class?
    def get_absolute_path(self, path, message = "path", depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVSkiaInterface.get_absolute_path]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Getting absolute path of [{path}], also checking its existence")

        # Get the absolute path
        path = self.utils.get_abspath(path, depth = ndepth)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Input {message} does not exist {path}")
        logging.info(STEP_SEPARATOR)
        return path

    # If we ever need any unique id..?
    def get_unique_id(self):
        return self.utils.get_unique_id()

    # # [ Experiments / sub projects ] # #

    # Get a pygradienter object with many workers for rendering
    def pygradienter(self, depth = PACKAGE_DEPTH, **kwargs):
        debug_prefix = "[MMVSkiaInterface.pygradienter]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Generating and returning one PyGradienter object")

        logging.info(STEP_SEPARATOR)
        return PyGradienter(self.mmv_main, depth = ndepth, **kwargs)
    
    # Returns a cmn_midi.py MidiFile class
    def get_midi_class(self):
        return MidiFile()

    # # [ Advanced ] # #

    def advanced_audio_processing_constants(self, where_decay_less_than_one, value_at_zero, depth = PACKAGE_DEPTH):
        debug_prefix = "[MMVSkiaInterface.advanced_audio_processing_constants]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        logging.info(f"{depth}{debug_prefix} Setting AudioProcessing constants to where_decay_less_than_one=[{where_decay_less_than_one}], value_at_zero=[{value_at_zero}]")

        self.mmv_main.audio.where_decay_less_than_one = where_decay_less_than_one
        self.mmv_main.audio.value_at_zero = value_at_zero


# Presets on the audio processing, like how and where to apply FFTs, frequencies we want
class AudioProcessingPresets:

    # Get this file main mmv class
    def __init__(self, mmv) -> None:
        self.mmv = mmv
    
    # Custom preset, sends directly those dictionaries
    def preset_custom(self, config: dict) -> None:
        self.mmv.mmv_main.audio_processing.config = config

    def preset_balanced(self) -> None:
        print("[AudioProcessingPresets.preset_balanced]", "Configuring MMV.AudioProcessing to get by matching musical notes frequencies on the FFT, balanced across high frequencies and bass")
        self.mmv.mmv_main.audio_processing.config = {
            0: {
                "sample_rate": 1000,
                "start_freq": 20,
                "end_freq": 500,
            },
            1: {
                "sample_rate": 40000,
                "start_freq": 500,
                "end_freq": 18000,
            }
        }

    # Do nothing FFT-regarding, useful for speed up on Piano Roll renders
    def preset_dummy(self) -> None:
        print("[AudioProcessingPresets.preset_dummy]", "Configuring MMV.AudioProcessing do nothing, only slice and calculate average value")
        self.mmv.mmv_main.audio_processing.config = {}
