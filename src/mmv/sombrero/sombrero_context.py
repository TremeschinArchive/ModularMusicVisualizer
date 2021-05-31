"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Store runtime functionality

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
from enum import Enum, auto


class KeyboardModes(Enum):
    ModeNone = auto()
    Mode2D = auto()
    Mode3D = auto()


class SombreroContext:
    def __init__(self, sombrero_mgl):
        self.sombrero_mgl = sombrero_mgl
        self.config = self.sombrero_mgl.config

        # Can be "reatime" or "render"
        self.mode = "realtime"

        # Window basics
        self.window_vsync = False
        self.show_gui = True

        # Resolution related
        self.gl_context = None
        self.width = 1920
        self.height = 1080
        self.fps = 60
        self.ssaa = 1
        self.msaa = 1
        self.quality = 10

        # Behavior variables
        self.intensity = 1
        self.time_speed = 1
        self.playback = 1
        self.debug_mode = False
        self.freezed_pipeline = False

        # Interactive
        self.shift_pressed = False
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.mouse_buttons_pressed = []

        # Windows
        self.window_show_menu = True
        self.LINUX_GNOME_PIXEL_SAVER_EXTENSION_WORKAROUND = False

        # Modules
        self.piano_roll = None
        self.camera3d = None
        self.camera2d = None

        # Default mode
        self.mode_realtime()

    # Set stuff for the render mode
    def mode_render(self):
        self.window_class = "headless"
        self.window_headless = True
        self.window_strict = False
        self.show_gui = False

    # Set stuff for realtime mode
    def mode_realtime(self):
        self.window_class = "glfw"
        self.window_headless = False
        self.window_strict = True
        self.keyboard_mode = KeyboardModes.Mode2D

    # # Technical functions

    # We are changing target fps, fix time
    def change_fps(self, new):
        self.sombrero_mgl.pipeline["mFrame"] *= (new / self.fps)
        self.fps = new
    
    # If new fps < 60, ratio should be higher
    def _fix_ratio_due_fps(self, ratio): return 1 - ((1 - ratio)**(60 / self.fps))
    def _fix_scalar_due_fps(self, scalar): return scalar * (self.fps / 60)
