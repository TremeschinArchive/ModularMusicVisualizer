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
import logging
import math
from enum import Enum, auto
from math import cos, sin

import imgui
import numpy as np
import pygame
from mmv.Sombrero.modules.base_module import BaseModule
from mmv.Sombrero.utils.interpolation import SmoothVariable


class Camera2D(BaseModule):
    GlobalX = np.array([1, 0], dtype = np.float32)
    GlobalY = np.array([0, 1], dtype = np.float32)
    GlobalCanonicalBase = np.array([GlobalX, GlobalY])
    AxisX, AxisY = 0, 1

    def __init__(self, sombrero_window):
        self.init(sombrero_window)
        self.sombrero_window = sombrero_window
        self.cfg = self.context.config["window"]["2D"]
        self.fix_due_fps = self.context._fix_ratio_due_fps
        self.reset()
        
    # # 2D Specific Info
    def reset(self):
        self.drag = SmoothVariable(np.array([0.0, 0.0]))
        self.intensity = SmoothVariable(1)
        self.rotation = SmoothVariable(0)
        self.zoom = SmoothVariable(1)

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

        # Cosine and sine, calculate once
        c = cos(self.rotation.value)
        s = sin(self.rotation.value)

        # mat2 rotation times the dx, dy vector
        drag_rotated = np.array([
            (dx * c) + (dy * -s),
            (dx * s) + (dy *  c),
        ]) * howmuch * inverse

        # Normalize dx step due aspect ratio
        drag_rotated[0] *= self.context.width / self.context.height

        # Add to target drag the dx, dy relative to current zoom and SSAA level
        self.drag += drag_rotated
        self.drag_momentum += drag_rotated

    def next(self):
    
        # Interpolate stuff
        self.rotation.next(ratio = self.fix_due_fps(self.cfg["rotation_responsiveness"]))
        self.zoom.next(ratio = self.fix_due_fps(self.cfg["zoom_responsiveness"]))
        self.drag.next(ratio = self.fix_due_fps(self.cfg["drag_responsiveness"]))
        self.drag_momentum *= self.cfg["drag_momentum"]

        # If we're still iterating towards target drag then we're dragging
        self.is_dragging = not np.allclose(self.drag.target, self.drag.value, rtol = 0.003)

        # Drag momentum
        if not 1 in self.context.mouse_buttons_pressed: self.drag.target += self.drag_momentum

    def key_event(self, key, action, modifiers):
        dpfx = "[Camera2D.key_event]"

        # Target rotation to the nearest 360° multiple (current minus negative remainder if you think hard enough)
        if (key == 67) and (action == 1):
            self.messages.add(f"{dpfx} [2D] (c) Reset rotation to [0°]", self.ACTION_MESSAGE_TIMEOUT)
            self.rotation.set_target(self.rotation.value - (math.remainder(self.rotation.value, 360)))

        if (key == 90) and (action == 1):
            self.messages.add(f"{dpfx} [2D] (z) Reset zoom to [1x]", self.ACTION_MESSAGE_TIMEOUT)
            self.zoom.set_target(1)

        if (key == 88) and (action == 1):
            self.messages.add(f"{dpfx} [2D] (x) Reset drag to [0, 0]", self.ACTION_MESSAGE_TIMEOUT)
            self.drag.set_target(np.array([0.0, 0.0]))

    def mouse_drag_event(self, x, y, dx, dy):
        if self.context.shift_pressed: self.zoom += (dy / 1000) * self.zoom.value
        elif self.context.alt_pressed: self.rotation += (dy / 80) / (2*math.pi)
        else: self.apply_rotated_drag(dx = dx, dy = dy, inverse = True)
    
    def gui(self):
        imgui.separator()
        imgui.text_colored("Camera 2D", 0, 1, 0)
        imgui.text(f"(x, y):    [{self.drag.value[0]:.3f}, {self.drag.value[1]:.3f}] => [{self.drag.target[0]:.3f}, {self.drag.target[1]:.3f}]")
        imgui.text(f"Intensity: [{self.intensity.value:.2f}] => [{self.intensity.target:.2f}]")
        imgui.text(f"Zoom:      [{self.zoom.value:.5f}x] => [{self.zoom.target:.5f}x]")
        imgui.text(f"UV Rotation:  [{math.degrees(self.rotation.value):.3f}°] => [{math.degrees(self.rotation.target):.3f}°]")

    def mouse_scroll_event(self, x_offset, y_offset):
        if self.context.shift_pressed:
            self.intensity += y_offset / 10

        elif self.context.ctrl_pressed and (not self.is_dragging_mode):
            change_to = self.context.ssaa + ((y_offset / 20) * self.context.ssaa)
            self.change_ssaa(change_to)

        elif self.context.alt_pressed:
            self.rotation -= y_offset * (math.pi) / (180 / 5)

        else:
            self.zoom -= (y_offset * 0.05) * self.zoom.value
        
    def mouse_position_event(self, x, y, dx, dy):
        pass