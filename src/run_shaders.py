"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Basic usage example of MMV

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

# Add current directory to PATH so we find the "mmv" package
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Continue imports
from watchdog.events import FileSystemEventHandler
from mmv.sombrero.sombrero_shader import *
from watchdog.observers import Observer
import mmv.common.cmn_any_logger
from dotmap import DotMap
from pathlib import Path
from tqdm import tqdm
import numpy as np
import itertools
import soundcard
import logging
import typer
import time
import mmv


# Watchdog for changes, reload shaders
class AnyModification(FileSystemEventHandler):
    def __init__(self, controller):
        self.controller = controller

    def on_modified(self, event):
        debug_prefix = "[AnyModification.on_modified]"
        logging.info(f"{debug_prefix} Some modification event [{event}], reloading shaders..")
        self.controller.sombrero_main._want_to_reload = True


class MMVShadersCLI:
    def __init__(self):
        debug_prefix = "[MMVShadersCLI.__init__]"
        self.sep = os.path.sep

        # # Initialize stuff

        # MMV interface
        self.mmv_package_interface = mmv.MMVPackageInterface()
        self.utils = self.mmv_package_interface.utils

        # Shaders interface and MGL
        self.sombrero_main = self.mmv_package_interface.get_sombrero()(mmv_interface = self.mmv_package_interface, master_shader = True)

        # Ensure FFmpeg on Windows
        self.mmv_package_interface.check_download_externals(target_externals = ["ffmpeg"])

        # IO defaults
        self._input_audio = self.mmv_package_interface.assets_dir / "free_assets" / "kawaii_bass.ogg"
        self._output_video = "rendered_shader.mkv"

        # Audio
        self._audio_batch_size = int(self.mmv_package_interface.config["audio"]["batch_size"])
        self._sample_rate = int(self.mmv_package_interface.config["audio"]["sample_rate"])
        self._override_record_device = None

        # Resolution, rendering
        self._width = 1920
        self._height = 1080
        self._fps = 60
        self._ssaa = 1.1
        self._msaa = 8
        self._multiplier = 2.0
        self._have_audio = True

        # Use default preset
        self._preset_name = "default"
        self.watchdog = True

    # # Configuration

    # Target width, height and framerate
    def resolution(self, 
        width: int = typer.Option(1920, help = "Output resolution width (horizontal pixel count)"),
        height: int = typer.Option(1080, help = "Output resolution height (vertical pixel count)"),
        fps: float = typer.Option(60, help = "Output frame rate in Frames Per Seconds (FPS)"),
    ):
        logging.info(f"[MMVShadersCLI.resolution] Set [width={width}] [height={height}] [fps={fps}]")
        self._width, self._height, self._fps = int(width), int(height), int(fps)

    # SuperSampling AntiAliasing SSAA
    def antialiasing(self, 
        ssaa: float = typer.Option(1.1, help = (
            "Internally render in target resolution multiplied by this, then downscale to target. "
            "Greately degrades performance but reduces jagged edges a lot, use 1.5 or 2 when final exporting "
            "and 1, 1.1, 1.2 for real time mode if you want more smoothness. Defaults to 1.1")),
        msaa: int = typer.Option(8, help = (
            "Multi Sampling Anti Aliasing, can only be 1, 2, 4 or 8."
        ))
    ):
        logging.info(f"[MMVShadersCLI.antialiasing] Set [ssaa={ssaa}] [msaa={msaa}]")
        self._ssaa, self._msaa = float(ssaa), int(msaa)

    def load(self, 
        preset: str = typer.Option("default", help = (
            "Load some preset, executes the python file under /src/mmv/shaders/presets/{name}.py")),
        file: str = typer.Option("", help = (
            "Load a raw shader from disk."
        )),
        watchdog: bool = typer.Option(True, help = (
            "Watch for main shader or Python preset file on disk file modifications, rebuilds and reloads shaders. Good for development of shaders."
        ))
    ):
        debug_prefix = "[MMVShadersCLI.preset]"
        self.watchdog = watchdog

        # User sent some file to be the main shader so we 
        if file:
            logging.info(f"{debug_prefix} Load raw shader!! Set [preset master shader={file}]")
            self._preset_name = None
        else:
            logging.info(f"{debug_prefix} Execute preset file!! Set [preset={preset}]")
            self._preset_name = preset

    def multiplier(self, 
        value: float = typer.Option(2.0, help = (
            "Multiply target interpolation values by this amount, yields more aggressiveness"
        ))
    ):
        logging.info(f"[MMVShadersCLI.multiplier] Set [multiplier={value}]")
        self._multiplier = float(value)

    # # Running, executing

    # Set SombreroMGL target settings
    def __sombrero_mgl_target_render_settings(self):
        self.sombrero_main.configure(width = self._width, height = self._height, ssaa = self._ssaa, fps = self._fps)

    def __configure_audio_processing(self):
        # Configure FFT TODO: advanced config?
        self.audio_source.audio_processing.configure(config = [
            {
                "original_sample_rate": 48000,
                "target_sample_rate": 1000,
                "start_freq": 80,
                "end_freq": 500,
            },
            {
                "original_sample_rate": 48000,
                "target_sample_rate": 48000,
                "start_freq": 500,
                "end_freq": 20000,
            }
        ])
        self.MMV_FFTSIZE = self.audio_source.audio_processing.FFT_length

    def __load_preset(self):
        debug_prefix = "[MMVShadersCLI.__load_preset]"

        # # Will we load preset file or raw file shader? 
        if self._preset_name is None:
            raise RuntimeError()  # Raw file
        
        else: # Preset file
            context = DotMap(_dynamic = False)
            context.cli = self
            context.interface = self.mmv_package_interface
            context.new_shader = self.sombrero_main.new_child
            context.shaders_dir = self.mmv_package_interface.shaders_dir
            context.assets_dir = self.mmv_package_interface.assets_dir
            context.create_piano_roll = self.sombrero_main.create_piano_roll
            context.render_layers = self.sombrero_main.macros.alpha_composite
            self.sombrero_main.reset()
            preset = __import__(f"mmv.shaders.presets.{self._preset_name}", fromlist = [self._preset_name])
            preset.generate(context)
            self.sombrero_main.finish()
                    
    # List capture devices by index
    def list_captures(self):
        debug_prefix = "[MMVShadersCLI.list_captures]"
        logging.info(f"{debug_prefix} Available devices to record audio:")
        for index, device in enumerate(soundcard.all_microphones(include_loopback = True)):
            logging.info(f"{debug_prefix} > ({index}) [{device.name}]")
        logging.info(f"{debug_prefix} :: Run [realtime] command with argument --cap N")

    # Display shaders real time
    def realtime(self,
        window_class: str = typer.Option("glfw", help = "ModernGL Window backend to use, see [https://moderngl-window.readthedocs.io/en/latest/guide/window_guide.html], values are [sdl2, pyglet, glfw, pyqt5], GLFW works dynshader mode so I advise that. Please install the others if you wanna use them [poetry add / pip install pysdl2, pyqt5 etc]"),
        cap: int = typer.Option(None, help = "Capture device index to override first loopback we find. Run command [list-captures] to see available indexes, None (empty) is to get automatically")
    ):
        debug_prefix = "[MMVShadersCLI.realtime]"
        self.__sombrero_mgl_target_render_settings()
        repo_dir = self.mmv_package_interface.MMV_PACKAGE_ROOT/".."/".."/"repo"
        self.mode = "view"

        # Start mgl window
        self.sombrero_main.window.create(
            window_class = window_class,
            msaa = self._msaa,
            vsync = False,
            icon = repo_dir/"icon.png"
        )

        # # Audio source Real Time
        self.audio_source = self.mmv_package_interface.get_audio_source_realtime()

        # Configure audio source
        self.audio_source.configure(
            batch_size = self._audio_batch_size,
            sample_rate = self._sample_rate,
            recorder_numframes = None,
            do_calculate_fft = True
        )

        # Search for loopback or get index of recorder device
        if (cap is None):
            self.audio_source.init(search_for_loopback = True)
        else:
            for index, device in enumerate(soundcard.all_microphones(include_loopback = True)):
                if index == cap:
                    self.audio_source.init(recorder_device = device)

        # self.__configure_audio_processing()
        self.__load_preset()

        # Start reading data
        # self.audio_source.start_async()
        self._core_loop()

    # Render config to video file
    def render(self,
        output_video: str = typer.Option("rendered_shader.mkv", help = (
            "Name of the final video"
        )),
        audio: str = typer.Option(None, help = "Which audio to use as source on file?"),
        no_audio: bool = typer.Option(False, help = "Only render the shader, please pass --seconds as well!"),
        seconds: float = typer.Option(30, help = "Render only the shader by this much seconds"),
    ):
        debug_prefix = "[MMVShadersCLI.render]"
        self._have_audio = not no_audio
        self.mode = "render"

        self._output_video = output_video
        if audio is not None:
            self._input_audio = audio
        else:
            if no_audio:
                self._input_audio = None
                self.total_steps = self._fps * seconds
                self.duration = seconds

        self.__sombrero_mgl_target_render_settings()

        # Set window mode to headless
        self.sombrero_main.window.create(
            window_class = "headless",
            strict = True,
            vsync = False,
            msaa = self._msaa,
        )

        # # Audio source File
        if self._have_audio:
            self.audio_source = self.mmv_package_interface.get_audio_source_file()

            # Configure audio source
            self.audio_source.configure(
                target_fps = self._fps,
                process_batch_size = self._audio_batch_size,
                sample_rate = self._sample_rate,
                do_calculate_fft = True,
            )

            # Read source audio file
            self.audio_source.init(audio_path = self._input_audio)

            # How much bars we'll have
            self.MMV_FFTSIZE = self.audio_source.audio_processing.FFT_length
            self.total_steps = self.audio_source.total_steps
            self.duration = self.audio_source.duration

        # self.__configure_audio_processing()
        self.__load_preset()
      
        # Get video encoder
        self.ffmpeg = self.mmv_package_interface.get_ffmpeg_wrapper()

        # Settings, see /src/mmv/common/wrappers/wrap_ffmpeg.py for what those do
        self.ffmpeg.configure_encoding(
            width = self._width,
            height = self._height,
            input_audio_source = self._input_audio,
            input_video_source = "pipe",
            output_video = self._output_video,
            framerate = self._fps,
            preset = self.mmv_package_interface.config["ffmpeg"]["preset"],
            crf = self.mmv_package_interface.config["ffmpeg"]["crf"],
            tune = self.mmv_package_interface.config["ffmpeg"]["tune"],
            vflip = self.mmv_package_interface.config["ffmpeg"]["vflip"],
            vcodec = "libx264",
            hwaccel = "auto",
            loglevel = "panic",
            pix_fmt = "rgb24",
            hide_banner = True,
            override = True,
            nostats = True,
            opencl = False,
        )
        self.ffmpeg.start()

        # Main routines
        self._core_loop()

    # Common main loop for both view and render modes
    def _core_loop(self):
        debug_prefix = "[MMVShadersCLI.render]"

        # Look for file changes
        if self.watchdog:
            logging.info(f"{debug_prefix} Starting watchdog")
            self.any_modification_watchdog = AnyModification(controller = self)
            sd = self.mmv_package_interface.shaders_dir
            paths = [
                sd / "presets", sd / "assets", sd / "sombrero",
                self.mmv_package_interface.runtime_dir,
            ]
            self.watchdog_observer = Observer()
            for path in paths: self.watchdog_observer.schedule(self.any_modification_watchdog, path = path, recursive = True)
            self.watchdog_observer.start()

        # FPS, manual vsync dealing
        self.start = time.time()
        self.fps_last_n = 120
        self.frame_times = [time.time() + i / self._fps for i in range(self.fps_last_n)]

        # Start audio source
        # self.audio_source.start()
        logging.info(f"{debug_prefix} Started audio source")

        # Render mode have progress bar
        if self.mode == "render":

            # Create progress bar
            self.progress_bar = tqdm(
                total = self.total_steps,
                # unit_scale = True,
                unit = " frames",
                dynamic_ncols = True,
                colour = '#38bed6',
                position = 0,
                smoothing = 0.3
            )

            # Set description
            self.progress_bar.set_description(
                f"Rendering [SSAA={self._ssaa}]({int(self._width * self._ssaa)}x{int(self._height * self._ssaa)})->({self._width}x{self._height})[{self.duration:.2f}s] MMV video"
            )

        # Main loop
        for step in itertools.count(start = 0):
            if self.sombrero_main._want_to_reload:
                self.__load_preset(); self.sombrero_main._want_to_reload = False

            # The time this loop is starting
            startcycle = time.time()

            # Next iteration of some audio reader
            # self.audio_source.next(step)

            # Get info to pipe, and the pipelined built info
            # pipeline_info = self.audio_source.get_info()
            pipelined = {}

            multiplier = self._multiplier * self.sombrero_main.window.intensity

            # Next iteration
            self.sombrero_main.next(custom_pipeline = pipelined)

            # Write current image to the video encoder
            if self.mode == "render":
                self.progress_bar.update(1)

                # Write to the FFmpeg stdin
                self.sombrero_main.read_into_subprocess_stdin(self.ffmpeg.subprocess.stdin)

                # Looped the audio one time, exit
                if step == self.total_steps - 2:
                    self.ffmpeg.subprocess.stdin.close()
                    break

            # View mode we just update window, print fps
            elif self.mode == "view":

                # The window received close command
                if self.sombrero_main.window.window_should_close:
                    self.audio_source.stop()
                    self.mmv_package_interface.thanks_message()
                    break

            if (not self.sombrero_main.window.vsync) and (self.mode == "view"):
                if (t := (1 / self.sombrero_main.fps) + startcycle - time.time()) >= 0: time.sleep(t)

# main function to use typer for CLI
def main():
    app = typer.Typer(chain = True)
    cli = MMVShadersCLI()
    app.command()(cli.resolution)
    app.command()(cli.antialiasing)
    app.command()(cli.multiplier)
    app.command()(cli.realtime)
    app.command()(cli.list_captures)
    app.command()(cli.render)
    app.command()(cli.load)
    app()

# This wouldn't be required but Windows :p
if __name__ == "__main__":
    main()
