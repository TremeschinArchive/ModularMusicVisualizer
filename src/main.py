"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Orchestrate MMV to be executed, technical part

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

from importlib import reload  
from dotmap import DotMap
import mmv.render_config
import itertools
import datetime
import typer
import time
import mmv


class MMVMain:
    def __init__(self):

        # Create classes
        self.mmv_package_interface = mmv.MMVPackageInterface()
        self.mmv_package_interface.main = self
        self.config = self.mmv_package_interface.config
        self.utils = self.mmv_package_interface.utils

        # Initiate SombreroMGL
        self.sombrero_mgl = self.mmv_package_interface.get_sombrero()(
            mmv_interface = self.mmv_package_interface, master_shader = True)
        self.context = self.sombrero_mgl.context 
        self.context.mmv_main = self
        self.current_preset = None   
        self.step = 0

    # "Secondary" context with easier bindings
    def __get_ctx(self):
        ctx = DotMap(_dynamic = False)
        ctx.main = self
        ctx.interface = self.mmv_package_interface
        ctx.context = self.context
        ctx.config = self.mmv_package_interface.config
        ctx.new_shader = self.sombrero_mgl.new_child
        ctx.shaders_dir = self.mmv_package_interface.shaders_dir
        ctx.sombrero_dir = self.mmv_package_interface.sombrero_dir
        ctx.assets_dir = self.mmv_package_interface.assets_dir
        ctx.create_piano_roll = self.sombrero_mgl.create_piano_roll
        ctx.render_layers = self.sombrero_mgl.macros.alpha_composite
        self.ctx = ctx
        return ctx

    # Load some preset directly by name # TODO: accept file
    def load_preset(self,
            name: str = typer.Option("default", help = "Preset name to load"),
            reset_time = True
        ):
        self.current_preset = name
        self.sombrero_mgl.reset()
        if reset_time: self.sombrero_mgl.time_zero()
        self.preset = __import__(f"mmv.shaders.presets.{name}", fromlist = [name])
        self.preset = reload(self.preset)  # Reload if file has changed
        self.preset.generate(self.__get_ctx())
        self.sombrero_mgl.finish()

    # Reload shaders (reload preset without resetting time)
    def reload_shaders(self): self.load_preset(self.current_preset, reset_time = False)

    # 
    def realtime(self):
        self.context.mode = "realtime"
        self._core_loop()

    # Render
    def render(self,
        audio: str = typer.Option(None, help = "Which audio to use as source on file?")
    ):
        self.context.mode = "render"
        self.context.mode_render()
        self.__get_ctx()
        
        # Assign instructions
        self.ctx.input_audio = audio

        # Get expected information for rendering
        self.expect = mmv.render_config.setup(self.ctx)
        self._core_loop()

    def _core_loop(self):
        debug_prefix = "[MMVMain._core_loop]"
        self.__get_ctx()
        self.sombrero_mgl.window.create()
        self.load_preset("potential")

        if hasattr(self.preset, "pipeline"): self.preset_custom_pipeline = self.preset.pipeline
        else: self.preset_custom_pipeline = lambda _: {}
        self.true_start = time.time()

        for step in itertools.count(start = 0):
            start_cycle = time.time()
            self.context.current_processing_time = step / self.context.fps

            # Render next image
            self.sombrero_mgl.next(custom_pipeline = self.preset_custom_pipeline(self.ctx))

            # Write into FFmpeg stdin for rendering final video
            if self.context.mode == "render":
                self.sombrero_mgl.stdout(self.expect.ffmpeg.stdin)
                self.expect.progress_bar.update()

                # Quit if out of steps
                if step == self.expect.total_steps:
                    self.sombrero_mgl.window.window_should_close = True
                    self.mmv_package_interface.thanks_message()
                    self.expect.ffmpeg.stdin.close()
                    while self.expect.ffmpeg.subprocess.poll() is None:
                        time.sleep(1)
                        print(f"{debug_prefix} [{str(datetime.datetime.now())}] FFmpeg process is still alive, waiting..")
                    print(f"\n{debug_prefix} Took: [{datetime.timedelta(seconds = time.time() - self.true_start)}]")
                    break

            # Manual VSYNC
            if (not self.context.window_vsync) and (self.context.mode == "realtime"):
                if (t := (1 / self.context.fps) + start_cycle - time.time()) >= 0: time.sleep(t)
def main():
    app = typer.Typer(chain = True)
    mmv_main = MMVMain()
    app.command()(mmv_main.load_preset)
    app.command()(mmv_main.realtime)
    app.command()(mmv_main.render)
    app()

if __name__ == "__main__":
    main()