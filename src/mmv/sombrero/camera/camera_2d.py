"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: 2D camera utility

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
from math import sin, cos
import numpy as np
import logging
import imgui
import math


class Camera2D:
    GlobalX = np.array([1, 0], dtype = np.float32)
    GlobalY = np.array([0, 1], dtype = np.float32)
    GlobalCanonicalBase = np.array([GlobalX, GlobalY])
    AxisX, AxisY = 0, 1

    def __init__(self, sombrero_window):
        self.sombrero_window = sombrero_window
        self.context = self.sombrero_window.context
        self.messages = self.sombrero_window.messages
        self.sombrero_mgl = self.sombrero_window.sombrero_mgl

        self.ACTION_MESSAGE_TIMEOUT = self.sombrero_window.ACTION_MESSAGE_TIMEOUT
        self.cfg = self.context.config["window"]["2D"]
        self.fix_due_fps = self.context._fix_ratio_due_fps
        self.reset()
        
    # # 2D Specific Info
    def reset(self):
        self.target_drag = np.array([0.0, 0.0])
        self.drag = np.array([0.0, 0.0])

        self.target_intensity = 1
        self.intensity = 1

        self.target_uv_rotation = 0
        self.uv_rotation = 0

        self.target_zoom = 1
        self.zoom = 1

        # Multiplier on top of multiplier, configurable real time
        self.drag_momentum = np.array([0.0, 0.0])

        self.is_dragging_mode = False
        self.is_dragging = False

    # Apply drag with the target rotation (because dx and dy are relative to the window itself not the rendered contents)
    def apply_rotated_drag(self, dx, dy, howmuch = 1, inverse = False):

        # Inverse drag? Feels more natural when mouse exclusivity is on
        inverse = -1 if inverse else 1

        # Add to the mmv_drag pipeline item the dx and dy multiplied by the square of the current zoom
        square_current_zoom = (self.sombrero_mgl.pipeline["m2DZoom"] ** 2)

        # dx and dy on zoom and SSAA
        dx = (dx * square_current_zoom) * self.context.ssaa
        dy = (dy * square_current_zoom) * self.context.ssaa

        # Cosine and sine
        c = cos(self.uv_rotation)
        s = sin(self.uv_rotation)

        # mat2 rotation times the dx, dy vector
        drag_rotated = np.array([
            (dx * c) + (dy * -s),
            (dx * s) + (dy * c)
        ]) * howmuch * inverse

        # Normalize dx step due aspect ratio
        drag_rotated[0] *= self.context.width / self.context.height

        # Add to target drag the dx, dy relative to current zoom and SSAA level
        self.target_drag += drag_rotated
        self.drag_momentum += drag_rotated

    def next(self):

        # Interpolate stuff
        self.uv_rotation += (self.target_uv_rotation - self.uv_rotation) * self.fix_due_fps(self.cfg["rotation_responsiveness"])
        self.zoom += (self.target_zoom - self.zoom) * self.fix_due_fps(self.cfg["zoom_responsiveness"])
        self.drag += (self.target_drag - self.drag) * self.fix_due_fps(self.cfg["drag_responsiveness"])
        self.drag_momentum *= self.cfg["drag_momentum"]

        # If we're still iterating towards target drag then we're dragging
        self.is_dragging = not np.allclose(self.target_drag, self.drag, rtol = 0.003)

        # Drag momentum
        if not 1 in self.context.mouse_buttons_pressed: self.target_drag += self.drag_momentum

    def key_event(self, key, action, modifiers):
        debug_prefix = "[Camera2D.key_event]"

        # Target rotation to the nearest 360° multiple (current minus negative remainder if you think hard enough)
        if (key == 67) and (action == 1):
            self.messages.add(f"{debug_prefix} [2D] (c) Reset rotation to [0°]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_uv_rotation = self.target_uv_rotation - (math.remainder(self.target_uv_rotation, 360))

        if (key == 90) and (action == 1):
            self.messages.add(f"{debug_prefix} [2D] (z) Reset zoom to [1x]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_zoom = 1

        if (key == 88) and (action == 1):
            self.messages.add(f"{debug_prefix} [2D] (x) Reset drag to [0, 0]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_drag = np.array([0.0, 0.0])

    def mouse_drag_event(self, x, y, dx, dy):
        if self.context.shift_pressed: self.target_zoom += (dy / 1000) * self.target_zoom
        elif self.context.alt_pressed: self.target_uv_rotation += (dy / 80) / (2*math.pi)
        else: self.apply_rotated_drag(dx = dx, dy = dy, inverse = True)
    
    def gui(self):
        imgui.text_colored("Camera 2D", 0, 1, 0)
        imgui.text(f"(x, y):    [{self.drag[0]:.3f}, {self.drag[1]:.3f}] => [{self.target_drag[0]:.3f}, {self.target_drag[1]:.3f}]")
        imgui.text(f"Intensity: [{self.intensity:.2f}] => [{self.target_intensity:.2f}]")
        imgui.text(f"Zoom:      [{self.zoom:.5f}x] => [{self.target_zoom:.5f}x]")
        imgui.text(f"UV Rotation:  [{math.degrees(self.uv_rotation):.3f}°] => [{math.degrees(self.target_uv_rotation):.3f}°]")
        imgui.separator()

    def mouse_scroll_event(self, x_offset, y_offset):
        if self.context.shift_pressed:
            self.target_intensity += y_offset / 10
        elif self.context.ctrl_pressed and (not self.is_dragging_mode):
            change_to = self.context.ssaa + ((y_offset / 20) * self.context.ssaa)
            self.change_ssaa(change_to)
        elif self.context.alt_pressed:
            self.target_uv_rotation -= y_offset * (math.pi) / (180 / 5)
        else:
            self.target_zoom -= (y_offset * 0.05) * self.target_zoom
        
    def mouse_position_event(self, x, y, dx, dy):
        pass