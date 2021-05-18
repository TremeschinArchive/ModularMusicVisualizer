"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: 3D camera utility

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
import quaternion
import imgui
import math

# Normalize safely some vector to 1, if zero return 0
def unit_vector(v):
    N = np.linalg.norm(v, ord = 1)
    if N == 0: N = 1
    return v / N

def angle_between(v1, v2):
    return np.arccos( np.dot(unit_vector(v1), unit_vector(v2)) )

Qfromvec = quaternion.from_vector_part
Qasvec = quaternion.as_vector_part

class Camera3D:
    ModeFreeCamera = "Free Camera"
    ModeGlobal = "Global Camera"
    Modes = [ModeGlobal, ModeFreeCamera]
    
    # Unit vectors as quaterions
    GlobalX = np.array([1, 0, 0], dtype = np.float32)
    GlobalY = np.array([0, 1, 0], dtype = np.float32)
    GlobalZ = np.array([0, 0, 1], dtype = np.float32)

    # Directions
    Up = GlobalZ
    Right = - GlobalY
    Forward = GlobalX

    GlobalCanonicalBase = np.array([GlobalX, GlobalZ, GlobalY])
    AxisX, AxisY, AxisZ = 0, 1, 2
    
    def cycle_mode(self):
        CM = Camera3D.Modes
        self.mode = CM[(CM.index(self.mode)+1) % len(CM)]

    def __repr__(self): return f"Camera3D: {self.__pointing()}"
    def __init__(self, sombrero_window):
        self.sombrero_window = sombrero_window
        self.messages = self.sombrero_window.messages
        self.sombrero_mgl = self.sombrero_window.sombrero_mgl
        self.ACTION_MESSAGE_TIMEOUT = self.sombrero_window.ACTION_MESSAGE_TIMEOUT
        self.cfg = self.sombrero_mgl.config["window"]["3D"]
        self.fix_due_fps = self.sombrero_window.sombrero_mgl._fix_ratio_due_fps

        # self.mode = Camera3D.ModeFreeCamera
        self.mode = Camera3D.ModeGlobal

        self.target_quaternion = np.quaternion(1, 0, 0, 0)
        self.quaternion = np.quaternion(1, 0, 0, 0)

        self.want_to_toll = 0
        self.roll = 0

        self.want_to_walk_unit_vector = np.array([0, 0, 0], dtype = np.float32)
        self.target_position = np.array([0, 0, 0], dtype = np.float32)
        self.position = np.array([0, 0, 0], dtype = np.float32)

        self.target_walk_speed = 1
        self.walk_speed = 1

        self.target_fov = 1
        self.fov = 1

        self.sensitivity = 1

    def _angle_vector_quaternion(self, angle, v):
        return np.quaternion( math.cos(angle/2), *((v* math.sin(angle/2)) / np.linalg.norm(v)) )

    @property
    # Free camera mode we rotate the global XYZ to where we are pointing now
    # so we have a free global->local coordinates conversion
    def canonical_base(self):
        R = quaternion.rotate_vectors(self.quaternion, Camera3D.GlobalCanonicalBase)
        R = quaternion.rotate_vectors(self._angle_vector_quaternion(self.roll, Camera3D.Forward), R)  # Apply roll
        return R
    
    @property
    # Where the camera is pointing XYZ relative to the center
    def pointing(self): return quaternion.rotate_vectors(self.quaternion, Camera3D.GlobalX)

    # Angle: radians; Axis: Camere3D.XAxis, .YAxis, .ZAxis or just 0, 1, 2
    def apply_rotation(self, angle, axis):
        # Get the rotation axis we'll rotate based on current basis
        # remember this base can be global or local
        # rot = self._angle_vector_quaternion(angle=-angle*2, v=self.canonical_base[axis])
        rot = self._angle_vector_quaternion(
            angle=-angle*2, v=quaternion.rotate_vectors(self.quaternion.conj(), self.canonical_base[axis]))

        # Rotate current quaternion
        self.target_quaternion = self.target_quaternion * rot

    # Rotate smoothly to target quaternion
    def do_slerp(self):
        self.quaternion = quaternion.slerp_evaluate(self.quaternion, self.target_quaternion, self.cfg["rotation_responsiveness"])

    # # Sombrero Window Functions

    def next(self):
        for index, vector in enumerate(self.canonical_base):
            self.target_position += vector \
                * self.fix_due_fps(0.1 * self.want_to_walk_unit_vector[index] * self.walk_speed)

        self.position += (self.target_position - self.position) * self.fix_due_fps(self.cfg["walk_responsiveness"])
        self.walk_speed += (self.target_walk_speed - self.walk_speed) * self.fix_due_fps(self.cfg["walk_responsiveness"])
        self.fov += (self.target_fov - self.fov) * self.fix_due_fps(self.cfg["zoom_responsiveness"])

        # Apply roll
        if self.want_to_toll != 0: self.apply_rotation(self.want_to_toll, Camera3D.AxisX)

        # Cancell roll relative to the camera, get angle between XY plane basically
        if self.mode == Camera3D.ModeGlobal:
            a = (math.pi / 2) - angle_between(self.canonical_base[2], Camera3D.GlobalZ)
            self.apply_rotation(a, Camera3D.AxisX)

        self.do_slerp()
        self.quaternion = np.normalized(self.quaternion)
        
    def key_event(self, key, action, modifiers):
        debug_prefix = "[Camera3d.key_event]"

        if action in [0, 1]:
            if (key == 87):  self.want_to_walk_unit_vector[0] =  action  # W
            if (key == 65):  self.want_to_walk_unit_vector[2] = -action  # A
            if (key == 83):  self.want_to_walk_unit_vector[0] = -action  # S 
            if (key == 68):  self.want_to_walk_unit_vector[2] =  action  # D
            if (key == 32):  self.want_to_walk_unit_vector[1] =  action  # Space
            if (key == 340): self.want_to_walk_unit_vector[1] = -action  # Shift
            if (key == 81):  self.want_to_toll = -self.fix_due_fps(action / 200)  # q
            if (key == 69):  self.want_to_toll =  self.fix_due_fps(action / 200)  # e
        
        if (key == 77) and (action == 1):
            self.messages.add(f"{debug_prefix} (m) Cycle modes", self.ACTION_MESSAGE_TIMEOUT * 4)
            self.cycle_mode()

        if (key == 66) and (action == 1):
            self.messages.add(f"{debug_prefix} (b) Reset roll to [0°]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_quaternion.x = 0

        if (key == 86) and (action == 1):
            self.messages.add(f"{debug_prefix} (v) Reset inclination to [90°]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_quaternion.y = 0
            
        if (key == 67) and (action == 1):
            self.messages.add(f"{debug_prefix} (c) Reset azimuth to [0°]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_quaternion.z = 0

        if (key == 88) and (action == 1):
            self.messages.add(f"{debug_prefix} (x) Reset camera to (0, 0, 0)", self.ACTION_MESSAGE_TIMEOUT)
            self.target_position = np.array([0.0, 0.0, 0.0], dtype = np.float32)

        if (key == 90) and (action == 1):
            self.messages.add(f"{debug_prefix} (z) Reset FOV to [1x]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_fov = 1

    def mouse_drag_event(self, x, y, dx, dy):
        if self.sombrero_window.ctrl_pressed: self.target_fov += (dy * 0.05) * self.target_fov
        if self.sombrero_window.alt_pressed: self.apply_rotation( self.fix_due_fps(dy/800), Camera3D.AxisX)

    def gui(self):
        imgui.text_colored("3D Related", 0, 1, 0)
        cp = self.pointing
        imgui.text(f"Mode: [{self.mode}]")
        imgui.text(f"Camera Pointing:   [{cp[0]:.2f}, {cp[1]:.2f}, {cp[2]:.2f}]")
        # cb = self.canonical_base
        # imgui.text(f"Canonical base:")
        # imgui.text(f" - X: [{cb[0]}]")
        # imgui.text(f" - Y: [{cb[1]}]")
        # imgui.text(f" - Z: [{cb[2]}]")
        imgui.text(f"Quaternion: [{self.quaternion.w:.3f}, {self.quaternion.x:.3f}, {self.quaternion.y:.3f}, {self.quaternion.z:.3f}]")
        imgui.text(f"Position:   [{self.target_position[0]:.3f}, {self.target_position[1]:.3f}, {self.target_position[2]:.3f}]")
        imgui.text(f"Walk speed: [{self.walk_speed:.3f}]")
        imgui.text(f"Roll: [{self.roll:.3f}]")

    def mouse_scroll_event(self, x_offset, y_offset):
        if self.sombrero_window.alt_pressed: self.target_fov -= (y_offset * 0.05) * self.target_fov
        elif self.sombrero_window.ctrl_pressed: self.cfg["mouse_sensitivity"] += (y_offset * 0.05) * self.cfg["mouse_sensitivity"]
        else: self.target_walk_speed += (y_offset * 0.05) * self.target_walk_speed

    def mouse_position_event(self, x, y, dx, dy):
        self.apply_rotation((-dx/500) * self.fov, Camera3D.AxisY)
        self.apply_rotation((-dy/500) * self.fov, Camera3D.AxisZ)
    