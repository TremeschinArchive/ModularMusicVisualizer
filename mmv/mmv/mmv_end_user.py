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
from mmv.pygradienter.pyg_main import PyGradienter
from mmv.mmv_generator import MMVGenerator
from mmv.common.cmn_midi import MidiFile
from mmv.common.cmn_utils import Utils
from mmv.mmv_image import MMVImage
from mmv.mmv_main import MMVMain
import subprocess
import tempfile
import shutil
import uuid
import time
import sys
import os


# Main wrapper class for the end user, facilitates MMV in a whole
class MMVEndUser:

    # Start default configs, creates wrapper classes
    def __init__(self, **kwargs) -> None:
        debug_prefix = "[MMVEndUser.__init__]"

        # # FIXME: Currently can't run on Python 3.9, skia-python don't have packages for it

        # Max python version, show info, assert, pretty print
        maximum_python_version = (3, 9)
        print(debug_prefix, f"Checking if Python <= {maximum_python_version}.. ", end = "", flush = True)
        assert sys.version_info <= maximum_python_version
        print("ok")

        # Main class of MMV
        self.mmv_main = MMVMain()

        # Utilities
        self.utils = Utils()

        # Start MMV classes that main connects them, do not run
        self.mmv_main.setup()

        # Configuring options
        self.quality_preset = QualityPreset(self)
        self.audio_processing = AudioProcessingPresets(self)
        self.post_processing = self.mmv_main.canvas.configure

        # Has the user chosen to watch the processing video realtime?
        self.mmv_main.context.watch_processing_video_realtime = kwargs.get("watch_processing_video_realtime", False)
        self.mmv_main.context.pixel_format = kwargs.get("pixel_format", "auto")
        self.mmv_main.context.audio_amplitude_multiplier = kwargs.get("audio_amplitude_multiplier", 1)
        self.mmv_main.context.skia_render_backend = kwargs["render_backend"]
        
        # Main module files directory (where __init__.py is)
        self.THIS_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.EXTERNALS_DIR = self.mmv_main.context.externals

        self.mmv_main.context.externals = self.EXTERNALS_DIR

        self.mmv_main.utils.mkdir_dne(self.EXTERNALS_DIR)

        # Append to PATH the 
        print(debug_prefix, f"Appending EXTERNALS_DIR to PATH: [{self.EXTERNALS_DIR}]")
        sys.path.append(self.EXTERNALS_DIR)

    # Execute MMV with the configurations we've done
    def run(self) -> None:
        print("[MMVEndUser.run]", f"Configuration phase done, executing MMVMain.run()..")
        self.mmv_main.run()

    # Define output video width, height and frames per second, defaults to 720p60
    def quality(self, width: int = 1280, height: int = 720, fps: int = 60, batch_size = 2048) -> None:
        debug_prefix = "[MMVEndUser.quality]"
        
        print(debug_prefix, f"Setting width={width} height={height} fps={fps} batch_size={batch_size}")
        
        self.mmv_main.context.width = width
        self.mmv_main.context.height = height
        self.mmv_main.context.fps = fps
        self.mmv_main.context.batch_size = batch_size
        self.width = width
        self.height = height
        self.resolution = [width, height]

        print(debug_prefix, "Creating canvas with that width and height")
        self.mmv_main.canvas.create_canvas()

    # Set the input audio file, raise exception if it does not exist
    def input_audio(self, path: str) -> None:
        print("[MMVEndUser.input_audio]", f"Audio file path: [{path}], getting absolute path..")
        self.mmv_main.context.input_file = self.get_absolute_path(path)
    
    # Set the input audio file, raise exception if it does not exist
    def input_midi(self, path: str) -> None:
        print("[MMVEndUser.input_midi]", f"MIDI file path: [{path}], getting absolute path..")
        self.mmv_main.context.input_midi = self.get_absolute_path(path)
    
    # Output path where we'll be saving the final video
    def output_video(self, path: str) -> None:
        print("[MMVEndUser.output_video]", f"Output video path: [{path}], getting absolute path..")
        self.mmv_main.context.output_video = self.utils.get_abspath(path)
    
    def offset_audio_steps(self, steps: int = 0):
        print("[MMVEndUser.offset_audio_steps]", f"Offset audio in N steps: [{steps}]")
        self.mmv_main.context.offset_audio_before_in_many_steps = steps
    
    # # [ MMV Objects ] # #
    
    # Add a given object to MMVAnimation content on a given layer
    def add(self, item, layer: int=0) -> None:
        debug_prefix = "[MMVEndUser.add]"

        # Make layers until this given layer if they don't exist
        print(debug_prefix, f"Making animations layer until N = [{layer}]")
        self.mmv_main.mmv_animation.mklayers_until(layer)

        # Check the type and add accordingly
        if self.utils.is_matching_type([item], [MMVImage]):
            print(debug_prefix, f"Add MMVImage object [{item}]")
            self.mmv_main.mmv_animation.content[layer].append(item)
            
        if self.utils.is_matching_type([item], [MMVGenerator]):
            print(debug_prefix, f"Add MMVGenerator object [{item}]")
            self.mmv_main.mmv_animation.generators.append(item)

    # Get a blank MMVImage object with the first animation layer build up
    def image_object(self) -> MMVImage:
        print("[MMVEndUser.image_object] Creating blank MMVImage object and initializing first animation layer, returning it afterwards")
        mmv_image_object = MMVImage(self.mmv_main)
        mmv_image_object.configure.init_animation_layer()
        return mmv_image_object

    # Get a blank MMVGenerator object
    def generator_object(self):
        print("[MMVEndUser.generator_object] Creating blank MMVGenerator object, returning it afterwards")
        return MMVGenerator(self.mmv_main)

    # # [ Utilities ] # #

    # Random file from a given path directory (loading random backgrounds etc)
    def random_file_from_dir(self, path):
        print("[MMVEndUser.random_file_from_dir]", "Get absolute path and returning random file from directory: [{payh}]")
        return self.utils.random_file_from_dir(self.utils.get_abspath(path))

    # Make the directory if it doesn't exist
    def make_directory_if_doesnt_exist(self, path: str) -> None:
        path = self.utils.get_abspath(path)
        self.utils.mkdir_dne(path)
    
    # Make the directory if it doesn't exist
    def delete_directory(self, path: str) -> None:
        path = self.utils.get_abspath(path)
        self.utils.rmdir(path)

    # Get the absolute path to a file or directory, absolute starts with / on *nix and LETTER:// on Windows
    def get_absolute_path(self, path, message = "path"):
        path = self.utils.get_abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Input {message} does not exist {path}")
        return path

    # If we ever need any unique id..? shorter than uuid4?
    def get_unique_id(self):
        return self.utils.get_string_md5(str(uuid.uuid4()))

    # # [ Experiments / sub projects ] # #

    # Get a pygradienter object with many workers for rendering
    def pygradienter(self, **kwargs):
        return PyGradienter(self.mmv_main, **kwargs)

    # # [ QOL ] # #

    # Make sure we have FFmpeg on Windows
    def download_check_ffmpeg(self, making_release = False):
        debug_prefix = "[MMVEndUser.download_check_ffmpeg]"

        # Temporary directory if needed
        self.temp_dir = tempfile.gettempdir()
        print(debug_prefix, f"Temp dir is: [{self.temp_dir}]")

        if getattr(sys, 'frozen', False):
            print(debug_prefix, "Not checking ffmpeg.exe because is executable build")
            return

        # If the code is being run on a Windows OS
        if self.mmv_main.utils.os == "windows" or making_release:

            if making_release:
                print(debug_prefix, "Getting FFmpeg for Windows because making_release=True")

            # Where we should find the ffmpeg binary
            FFMPEG_FINAL_BINARY = self.EXTERNALS_DIR + "/ffmpeg.exe"

            # If we don't have FFmpeg binary on externals dir
            if not os.path.isfile(FFMPEG_FINAL_BINARY):

                # Get the latest release number of ffmpeg
                ffmpeg_release = self.mmv_main.download.get_html_content("https://www.gyan.dev/ffmpeg/builds/release-version")
                print(debug_prefix, f"FFmpeg release number is [{ffmpeg_release}]")

                # Where we'll save the compressed zip of FFmpeg
                ffmpeg_7z = self.temp_dir + f"/ffmpeg-{ffmpeg_release}-essentials_build.7z"

                # Download FFmpeg build
                self.mmv_main.download.wget(
                    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z",
                    ffmpeg_7z, f"FFmpeg v={ffmpeg_release}"
                )

                # Extract the files
                self.mmv_main.download.extract_file(ffmpeg_7z, self.temp_dir)

                # Where the FFmpeg binary is located
                ffmpeg_bin = ffmpeg_7z.replace(".7z", "") + "/bin/ffmpeg.exe"

                # Move to this directory
                self.mmv_main.utils.move(ffmpeg_bin, FFMPEG_FINAL_BINARY)

            else:
                print(debug_prefix, "Already have [ffmpeg.exe] downloaded and extracted")
        else:
            print(debug_prefix, "You are using Linux, please make sure you have FFmpeg package installed on your distro")

    # Make sure we have FFmpeg on Windows
    """
    kwargs: {
        "sf": str, "feepats"
            The soundfont to use
        "skip_fluidsynth_dep": bool, False
            Don't check for fluidsynth before downloading the soundfonts
        "skip_prompt": bool, False
            Don't ask the user if they want to run the mkdir and ln commands
    }
    """
    def download_and_link_freepats_general_midi_soundfont(self, **kwargs):
        debug_prefix = "[MMVEndUser.download_and_link_midi_soundfont]"

        skip_fluidsynth_dep = kwargs.get("skip_fluidsynth_dep", False)
        skip_prompt = kwargs.get("skip_prompt", False)
        sf = kwargs.get("sf", "freepats")

        # Dunno how to make it work on Windows
        if self.mmv_main.utils.os == "windows":
            print(debug_prefix, "This is not currently supported on Windows, don't know where Fluid Synth will check for the soundfont sf2 files, help needed")
            sys.exit(-1)

        elif self.mmv_main.utils.os in ["linux", "darwin"]:
            # Check for fluidsynth
            if not skip_fluidsynth_dep:
                if not self.mmv_main.utils.has_executable_with_name("fluidsynth"):
                    raise RuntimeError("Please install fluidsyth package from your distro, no point in downloading midi soundfonts and not being able to use them. Pass skip_fluidsynth_dep=True to this function to ignore this")
            else:
                print(debug_prefix, "skip_fluidsynth_dep=True, RUNNING REQUIRED COMMANDS AUTOMATICALLY")

        # FreePats General MIDI sound set
        if sf == "freepats":

            # # # [ IMPORTANT ] # # # 
            # # # [ IMPORTANT ] # # # 

            # See their license http://freepats.zenvoid.org/licenses.html
            print(debug_prefix, "\n\n[IMPORTANT] [IMPORTANT] SEE FREEPATS GENERAL MIDI SOUND SET LICENSE AT: http://freepats.zenvoid.org/licenses.html BEFORE USING [IMPORTANT] [IMPORTANT]\n")
            
            # # # [ IMPORTANT ] # # # 
            # # # [ IMPORTANT ] # # # 

            name = "FreePats General MIDI sound set"

            # File names
            version_tar_xz = "FreePatsGM-SF2-20200814.tar.xz"
            version_tar = version_tar_xz.replace(".tar.xz", ".tar")

            # Paths
            soundfont_tar_xz = f"{self.EXTERNALS_DIR}/{version_tar_xz}"
            soundfont_tar = f"{self.EXTERNALS_DIR}/{version_tar}"

            # Already downloaded files
            external_files = os.listdir(self.EXTERNALS_DIR)

            print(debug_prefix, "Externals files are:", external_files)

            # http://freepats.zenvoid.org/SoundSets/FreePats-GeneralMIDI/

            if not version_tar in external_files:
                print(debug_prefix, f"Soundfont {version_tar} not in externals")

                if not version_tar_xz in external_files:
                    print(debug_prefix, f"Soundfont {soundfont_tar_xz} not in externals")

                    # Download "FreePats General MIDI sound set"
                    self.mmv_main.download.wget(
                        f"http://freepats.zenvoid.org/SoundSets/FreePats-GeneralMIDI/{version_tar_xz}",
                        version_tar_xz, f"\"{name}\" File Name = {version_tar_xz}"
                    )

                # Extract the tar xz files
                self.mmv_main.download.extract_file(soundfont_tar_xz, self.EXTERNALS_DIR)

            # Where the stuff will be
            extracted_no_extension = version_tar_xz.replace(".tar.xz", "")
            extracted_file_name = extracted_no_extension.replace("-SF2", "")
            extracted_folder = f"{self.EXTERNALS_DIR}/{extracted_no_extension}"
            freepats_sf2 = f"{extracted_folder}/{extracted_file_name}.sf2"

            # Extract if we need so
            if not os.path.isdir(extracted_folder):
                # Extract the tar extracted from tar xz
                print(debug_prefix, f"Extracting to folder [{extracted_folder}]")
                self.mmv_main.download.extract_file(soundfont_tar, self.EXTERNALS_DIR)
            else:
                print(debug_prefix, f"Extracted folder [{extracted_folder}] already exists, skipping extracting..")
    
            print(debug_prefix, f"Downloaded sf2 in [{freepats_sf2}]")

            dot_fluidsynth = self.mmv_main.utils.get_abspath("~/.fluidsynth")
            default_soundfont = f"{dot_fluidsynth}/default_sound_font.sf2"

            if os.path.exists(default_soundfont):
                print(debug_prefix, f"Default sound font file on [{default_soundfont}] already exists, assuming it's already configured, returning this function..")
                return

            # The two commands
            command1 = ["mkdir", "-p", dot_fluidsynth]
            command2 = ["ln", "-s", freepats_sf2, default_soundfont]

            # Assume question="y" because skip_prompt kwargs was passed
            if skip_prompt:
                question = "y"

            # Ask the question
            else:
                # Pretty print
                print("\n" + ("-" * shutil.get_terminal_size()[0]))

                question = input(f"\n  We downloaded the FreePats General MIDI sound set to the directory [{freepats_sf2}], for fluidsynth to find it we have to link it to a default place, are you sure you want to run the following two commands: \n\n {command1}\n\n {command2}\n\n > Answer (y) for yes, anything else for no: ")

                print()
                
            # Run the two commands if answer was yes
            if question == "y":
                print(debug_prefix, "Running command", command1)
                subprocess.check_call(command1)

                print(debug_prefix, "Running command", command2)
                subprocess.check_call(command2)
            else:
                print(debug_prefix, "Question answer was anything but (y), ignoring and not linking FreePats")
    
    # Returns a cmn_midi.py MidiFile class
    def get_midi_class(self):
        return MidiFile()

# Presets on width and height
class QualityPreset:

    # Get this file main mmv class
    def __init__(self, mmv) -> None:
        self.mmv_main = mmv
    
    # Standard definition, 480p @ 24 fps
    def sd24(self) -> None:
        print("[QualityPreset.sd24]", "Setting MMVContext [width=854], [height=480], [fps=24]")
        self.mmv_main.main.context.width = 854 
        self.mmv_main.main.context.height = 480
        self.mmv_main.main.context.fps = 24
    
    # (old) HD definition, 720p @ 30 fps
    def hd30(self) -> None:
        print("[QualityPreset.hd30]", "Setting MMVContext [width=1280], [height=720], [fps=30]")
        self.mmv_main.main.context.width = 1280 
        self.mmv_main.main.context.height = 720
        self.mmv_main.main.context.fps = 30
    
    # Full HD definition, 1080p @ 60 fps
    def fullhd60(self) -> None:
        print("[QualityPreset.fullhd60]", "Setting MMVContext [width=1920], [height=1080], [fps=60]")
        self.mmv_main.main.context.width = 1920 
        self.mmv_main.main.context.height = 1080
        self.mmv_main.main.context.fps = 60

    # Quad HD (4x720p) definition, 1440p @ 60 fps
    def quadhd60(self) -> None:
        print("[QualityPreset.quadhd60]", "Setting MMVContext [width=2560], [height=1440], [fps=60]")
        self.mmv_main.main.context.width = 2560
        self.mmv_main.main.context.height = 1440
        self.mmv_main.main.context.fps = 60


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
            # 0: {
            #     "sample_rate": 40000,
            #     "get_frequencies": "musical",
            #     "start_freq": 20,
            #     "end_freq": 10000,
            #     "nbars": "original",
            # }
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
