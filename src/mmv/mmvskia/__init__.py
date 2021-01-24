"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
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

from mmv.mmvskia.mmv_skia_generator import MMVSkiaGenerator
from mmv.mmvskia.pygradienter.pyg_main import PyGradienter
from mmv.mmvskia.mmv_skia_image import MMVSkiaImage
from mmv.common.cmn_constants import STEP_SEPARATOR
print("[mmvskia.__init__.py package] Importing probably heaviest dependency [MMVSkiaMain], Skia might take a bit to load so does numpy, opencv etc..")
from mmv.mmvskia.mmv_skia_main import MMVSkiaMain
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
    # of MMV*Main to every other sub class so if we access self.mmv_skia_main.mmvskia_interface we are accessing this
    # file here, MMVSkiaInterface, and we can quickly refer to the most top level package by doing
    # self.mmv_skia_main.mmvskia_interface.top_level_interface, since this interface here is just the MMVSkia 
    # interface for the mmvskia package while the top level one manages both MMVSkia and MMVShader
    #
    def __init__(self, top_level_interace, **kwargs):
        debug_prefix = "[MMVSkiaInterface.__init__]"

        self.top_level_interace = top_level_interace
        self.os = self.top_level_interace.os

        # Where this file is located, please refer using this on the whole package
        # Refer to it as self.mmv_skia_main.mmvskia_interface.MMV_SKIA_ROOT at any depth in the code
        # This deals with the case we used pyinstaller and it'll get the executable path instead
        if getattr(sys, 'frozen', True):    
            self.MMV_SKIA_ROOT = os.path.dirname(os.path.abspath(__file__))
            logging.info(f"{debug_prefix} Running directly from source code")
            logging.info(f"{debug_prefix} Modular Music Visualizer Python package [__init__.py] located at [{self.MMV_SKIA_ROOT}]")
        else:
            self.MMV_SKIA_ROOT = os.path.dirname(os.path.abspath(sys.executable))
            logging.info(f"{debug_prefix} Running from release (sys.executable..?)")
            logging.info(f"{debug_prefix} Modular Music Visualizer executable located at [{self.MMV_SKIA_ROOT}]")

        # # Prelude configuration

        prelude_file = f"{self.MMV_SKIA_ROOT}{os.path.sep}mmv_skia_prelude.toml"
        logging.info(f"{debug_prefix} Attempting to load prelude file located at [{prelude_file}], we cannot continue if this is wrong..")

        with open(prelude_file, "r") as f:
            self.prelude = toml.loads(f.read())

        # Log prelude configuration
        logging.info(f"{debug_prefix} Prelude configuration is: {self.prelude}")

        # # # Create MMV classes and stuff

        # Main class of MMV and tart MMV classes that main connects them, do not run
        self.mmv_skia_main = MMVSkiaMain(interface = self)
        self.mmv_skia_main.setup()

        # Utilities
        self.utils = Utils()

        # Configuring options
        self.audio_processing = AudioProcessingPresets(self)
        self.post_processing = self.mmv_skia_main.canvas.configure

        # Log a separator to mark the end of the __init__ phase
        logging.info(f"{debug_prefix} Initialize phase done!")
        logging.info(STEP_SEPARATOR)

        self.configure_mmv_skia_main()
        self.CONFIGURED_PIPE_VIDEO_TO = False

        # Quit if code flow says so
        if self.prelude["flow"]["stop_at_interface_init"]:
            logging.critical(f"{debug_prefix} Not continuing because stop_at_interface_init key on prelude.toml is True")
            sys.exit(0)

    # Read the function body for more info
    def configure_mmv_skia_main(self, **kwargs):

        # Has the user chosen to watch the processing video realtime?
        self.mmv_skia_main.context.audio_amplitude_multiplier = kwargs.get("audio_amplitude_multiplier", 1)
        self.mmv_skia_main.context.skia_render_backend = kwargs.get("render_backend", "gpu")
        self.mmv_skia_main.context.max_images_on_pipe_buffer = kwargs.get("max_images_on_pipe_buffer", 20)
        self.mmv_skia_main.context.show_preview_window = kwargs.get("show_preview_window", False)
        self.mmv_skia_main.context.render_to_video = kwargs.get("render_to_video", True)

        if (not self.mmv_skia_main.context.show_preview_window) and (not self.mmv_skia_main.context.render_to_video):
            raise RuntimeError("Executing MMV without preview window and without extracting images will do nothing..")

    # Set MMVSkiaMain's ffmpeg attribute to the one the user configured
    def pipe_video_to(self, pipe_video_to):
        debug_prefix = "[MMVSkiaInterface.pipe_video_to]"

        logging.info(STEP_SEPARATOR)

        # Log action
        logging.info(f"{debug_prefix} Set pipe to wrapper to MMVSkiaMain")

        # Assign
        self.mmv_skia_main.pipe_video_to = pipe_video_to
        self.CONFIGURED_PIPE_VIDEO_TO = True

    # Execute MMV with the configurations we've done
    def run(self) -> None:
        debug_prefix = "[MMVSkiaInterface.run]"

        logging.info(STEP_SEPARATOR)

        # Log action
        logging.info(f"{debug_prefix} Configuration phase done, executing MMVSkiaMain.run()..")

        # Run configured mmv_skia_main class
        self.mmv_skia_main.run()

    # Define output video width, height and frames per second, defaults to 720p60
    def quality(self, width: int = 1280, height: int = 720, fps: int = 60) -> None:
        debug_prefix = "[MMVSkiaInterface.quality]"

        
        logging.info(f"{debug_prefix} Setting width={width} height={height} fps={fps}")
        
        # Assign values
        self.mmv_skia_main.context.width = width
        self.mmv_skia_main.context.height = height
        self.mmv_skia_main.context.fps = fps
        self.width = width
        self.height = height
        self.resolution = [width, height]
        self.fps = fps

        # Create or reset a mmv canvas with that target resolution
        logging.info(f"{debug_prefix} Creating / resetting canvas with that width and height")
        self.mmv_skia_main.canvas.create_canvas()
        logging.info(STEP_SEPARATOR)

    # Configure the overhaul FFT quality (batch size)
    def fft(self, batch_size = 2048) -> None:
        debug_prefix = "[MMVSkiaInterface.quality]"


        logging.info(f"{debug_prefix} Set FFT batch size to [{batch_size}]")

        self.mmv_skia_main.context.batch_size = batch_size
        logging.info(STEP_SEPARATOR)

    # Set the input audio file, raise exception if it does not exist
    def input_audio(self, path: str) -> None:
        debug_prefix = "[MMVSkiaInterface.input_audio]"


        # Log action, do action
        logging.info(f"{debug_prefix} Set audio file path: [{path}], getting absolute path..")
        self.mmv_skia_main.context.input_audio_file = self.get_absolute_path(path)
        logging.info(STEP_SEPARATOR)
    
    # Set the input audio file, raise exception if it does not exist
    def input_midi(self, path: str) -> None:
        debug_prefix = "[MMVSkiaInterface.input_midi]"


        # Log action, do action
        logging.info(f"{debug_prefix} Set MIDI file path: [{path}], getting absolute path..")
        self.mmv_skia_main.context.input_midi = self.get_absolute_path(path)
        logging.info(STEP_SEPARATOR)
    
    # Output path where we'll be saving the final video
    def output_video(self, path: str) -> None:
        debug_prefix = "[MMVSkiaInterface.output_video]"


        # Log action, do action
        logging.info(f"{debug_prefix} Set output video path: [{path}], getting absolute path..")
        self.mmv_skia_main.context.output_video = self.utils.get_absolute_realpath(path)
        logging.info(STEP_SEPARATOR)
    
    # Offset where we cut the audio for processing, mainly for interpolation latency compensation
    def offset_audio_steps(self, steps: int = 0):
        debug_prefix = "[MMVSkiaInterface.offset_audio_steps]"


        # Log action, do action
        logging.info(f"{debug_prefix} Offset audio in N steps: [{steps}]")
        self.mmv_skia_main.context.offset_audio_before_in_many_steps = steps
        logging.info(STEP_SEPARATOR)
    
    # # [ MMV Objects ] # #
    
    # Add a given object to MMVSkiaAnimation content on a given layer
    def add(self, item, layer: int = 0) -> None:
        debug_prefix = "[MMVSkiaInterface.add]"


        # Make layers until this given layer if they don't exist
        logging.info(f"{debug_prefix} Making animations layer until N = [{layer}]")
        self.mmv_skia_main.mmv_skia_animation.mklayers_until(layer)

        # Check the type and add accordingly
        if self.utils.is_matching_type([item], [MMVSkiaImage]):
            logging.info(f"{debug_prefix} Add MMVSkiaImage object [{item}]")
            self.mmv_skia_main.mmv_skia_animation.content[layer].append(item)
            
        if self.utils.is_matching_type([item], [MMVSkiaGenerator]):
            logging.info(f"{debug_prefix} Add MMVSkiaGenerator object [{item}]")
            self.mmv_skia_main.mmv_skia_animation.generators.append(item)

        logging.info(STEP_SEPARATOR)

    # Get a blank MMVSkiaImage object with the first animation layer build up
    def image_object(self) -> MMVSkiaImage:
        debug_prefix = "[MMVSkiaInterface.image_object]"


        # Log action
        logging.info(f"{debug_prefix} Creating blank MMVSkiaImage object and initializing first animation layer, returning it afterwards")
        
        # Create blank MMVSkiaImage, init the animation layers for the user
        mmv_skia_image_object = MMVSkiaImage(self.mmv_skia_main)
        mmv_skia_image_object.configure.init_animation_layer()

        # Return a pointer to the object
        logging.info(STEP_SEPARATOR)
        return mmv_skia_image_object

    # Get a blank MMVSkiaGenerator object
    def generator_object(self):
        debug_prefix = "[MMVSkiaInterface.generator_object]"


        # Log action
        logging.info(f"{debug_prefix} Creating blank MMVSkiaGenerator object, returning it afterwards")

        # Create blank MMVSkiaGenerator, return a pointer to the object
        logging.info(STEP_SEPARATOR)
        return MMVSkiaGenerator(self.mmv_skia_main)

    # # [ Utilities ] # #

    # Random file from a given path directory (loading random backgrounds etc)
    def random_file_from_dir(self, path):
        debug_prefix = "[MMVSkiaInterface.random_file_from_dir]"


        logging.info(f"{debug_prefix} Get absolute path and returning random file from directory: [{path}]")

        logging.info(STEP_SEPARATOR)
        return self.utils.random_file_from_dir(self.utils.get_absolute_realpath(path))

    # Make the directory if it doesn't exist
    def make_directory_if_doesnt_exist(self, path: str, silent = True) -> None:
        debug_prefix = "[MMVSkiaInterface.make_directory_if_doesnt_exist]"


        # Log action
        logging.info(f"{debug_prefix} Make directory if doesn't exist [{path}], get absolute realpath and mkdir_dne")

        # Get absolute and realpath, make directory if doens't exist (do the action)
        path = self.utils.get_absolute_realpath(path, silent = silent)
        self.utils.mkdir_dne(path)
        logging.info(STEP_SEPARATOR)
    
    # Make the directory if it doesn't exist
    def delete_directory(self, path: str, silent = False) -> None:
        debug_prefix = "[MMVSkiaInterface.delete_directory]"


        # Log action
        logging.info(f"{debug_prefix} Delete directory [{path}], get absolute realpath and rmdir")

        # Get absolute and realpath, delete directory (do the action)
        path = self.utils.get_absolute_realpath(path, silent = silent)
        self.utils.rmdir(path)
        logging.info(STEP_SEPARATOR)

    # Get the absolute path to a file or directory, absolute starts with / on *nix and LETTER:// on Windows
    # we expect it to exist so we quit if don't since this is the interface class?
    def get_absolute_path(self, path, message = "path"):
        debug_prefix = "[MMVSkiaInterface.get_absolute_path]"


        # Log action
        logging.info(f"{debug_prefix} Getting absolute path of [{path}], also checking its existence")

        # Get the absolute path
        path = self.utils.get_absolute_realpath(path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Input {message} does not exist {path}")
        logging.info(STEP_SEPARATOR)
        return path

    # If we ever need any unique id..?
    def get_unique_id(self):
        return self.utils.get_unique_id()

    # # [ Experiments / sub projects ] # #

    # Get a pygradienter object with many workers for rendering
    def pygradienter(self, **kwargs):
        debug_prefix = "[MMVSkiaInterface.pygradienter]"


        # Log action
        logging.info(f"{debug_prefix} Generating and returning one PyGradienter object")

        logging.info(STEP_SEPARATOR)
        return PyGradienter(self.mmv_skia_main, **kwargs)
    
    # Returns a cmn_midi.py MidiFile class
    def get_midi_class(self):
        return MidiFile()

    # # [ Advanced ] # #

    def advanced_audio_processing_constants(self, where_decay_less_than_one, value_at_zero):
        debug_prefix = "[MMVSkiaInterface.advanced_audio_processing_constants]"


        # Log action
        logging.info(f"{debug_prefix} Setting AudioProcessing constants to where_decay_less_than_one=[{where_decay_less_than_one}], value_at_zero=[{value_at_zero}]")

        self.mmv_skia_main.audio.where_decay_less_than_one = where_decay_less_than_one
        self.mmv_skia_main.audio.value_at_zero = value_at_zero


# Presets on the audio processing, like how and where to apply FFTs, frequencies we want
class AudioProcessingPresets:

    # Get this file main mmv class
    def __init__(self, mmv) -> None:
        self.mmv = mmv
    
    # Custom preset, sends directly those dictionaries
    def preset_custom(self, config: dict) -> None:
        self.mmv.mmv_skia_main.audio_processing.config = config

    def preset_balanced(self) -> None:
        print("[AudioProcessingPresets.preset_balanced]", "Configuring MMV.AudioProcessing to get by matching musical notes frequencies on the FFT, balanced across high frequencies and bass")
        self.mmv.mmv_skia_main.audio_processing.config = {
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
        self.mmv.mmv_skia_main.audio_processing.config = {}
