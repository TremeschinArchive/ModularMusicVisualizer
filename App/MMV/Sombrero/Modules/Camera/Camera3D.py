"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

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
import math
from enum import Enum, auto
from math import cos, sin

import imgui
import numpy as np
import quaternion
from MMV.Sombrero.Modules.BaseModule import BaseModule
from MMV.Sombrero.Utils.Interpolation import SmoothVariable


# Normalize safely some vector to 1, if zero return 0
def unit_vector(v):
    N = np.linalg.norm(v, ord = 1)
    if N == 0: N = 1
    return v / N

# Angle between two vectors, used for cancelling roll on GlobalCamera mode
def angle_between(v1, v2):
    return np.arccos( np.dot(unit_vector(v1), unit_vector(v2)) )


# Shorthands for quaternions functions
Qfromvec = quaternion.from_vector_part
Qasvec = quaternion.as_vector_part


class Camera3D(BaseModule):
    ModeFreeCamera = "Free Camera"
    ModeGlobal = "Global Camera"
    
    # Unit vectors as quaterions
    GlobalX = np.array([1, 0, 0], dtype = np.float32)
    GlobalY = np.array([0, 1, 0], dtype = np.float32)
    GlobalZ = np.array([0, 0, 1], dtype = np.float32)

    # Directions
    Up = GlobalZ
    Right = - GlobalY
    Forward = GlobalX

    # Sorted and unsorted attributes
    GlobalStandardBase = np.array([GlobalX, GlobalZ, GlobalY])
    Modes = [ModeGlobal, ModeFreeCamera]
    AxisX, AxisY, AxisZ = 0, 1, 2
    
    # Change between Camera3D.Modes
    def cycle_mode(self):
        CM = Camera3D.Modes
        self.mode = CM[(CM.index(self.mode)+1) % len(CM)]

    def __repr__(self): return f"Camera3D: {self.__pointing()}"
    def __init__(self, SombreroWindow):
        self.init(SombreroWindow)
        self.cfg = self.SombreroContext.LiveConfig["window"]["3D"]
        self.fix_due_fps = self.SombreroContext._fix_ratio_due_fps
        self.reset()
        
    # # 3D Specific Info
    def reset(self):
        self.mode = Camera3D.ModeGlobal

        self.target_quaternion = np.quaternion(1, 0, 0, 0)
        self.quaternion = np.quaternion(1, 0, 0, 0)

        # Direction we'll walk or roll, kinda like a joystick config
        self.want_to_walk_unit_vector = np.array([0, 0, 0], dtype = np.float32)
        self.want_to_roll = 0

        self.position = SmoothVariable(np.array([0, 0, 0], dtype = np.float32))
        self.sensitivity = SmoothVariable(1.0)
        self.speed = SmoothVariable(1.0)
        self.roll = SmoothVariable(0)
        self.fov = SmoothVariable(1)

    # Create one quaternion from an angle and vector, note the rotation is based
    # on the plane normal to this vector
    def _angle_vector_quaternion(self, angle, v):
        return np.quaternion( math.cos(angle/2), *((v* math.sin(angle/2)) / np.linalg.norm(v)) )

    @property
    # Current standard base applied on where the camera is pointing
    def standard_base(self):
        R = quaternion.rotate_vectors(self.quaternion, Camera3D.GlobalStandardBase)
        R = quaternion.rotate_vectors(self._angle_vector_quaternion(self.roll.value, Camera3D.Forward), R)  # Apply roll
        return R
    
    @property
    # Where the camera is pointing XYZ relative to the center
    def pointing(self): return quaternion.rotate_vectors(self.quaternion, Camera3D.GlobalX)

    # Angle: radians; Axis: Camere3D.XAxis, .YAxis, .ZAxis or just 0, 1, 2
    def apply_rotation(self, angle, axis):
        # Get the rotation axis we'll rotate based on current basis, I don't know why the conjugate is
        # really needed but it seems to be the case
        rot = self._angle_vector_quaternion(
            angle=-angle*2, v=quaternion.rotate_vectors(self.quaternion.conj(), self.standard_base[axis]))

        # Rotate current quaternion, note the order of operation matters for accumulating the rotations!
        self.target_quaternion = self.target_quaternion * rot

    # Rotate smoothly to target quaternion, call quaternion's spherical linear interpolation
    def do_slerp(self):
        self.quaternion = quaternion.slerp_evaluate(self.quaternion, self.target_quaternion, self.cfg["rotation_responsiveness"])

    # # Sombrero Window Functions

    # Next iteration
    def next(self):

        # Walk the camera if WASD Shift Space are pressed
        for index, vector in enumerate(self.standard_base):
            self.position += vector \
                * self.fix_due_fps(0.1 * self.want_to_walk_unit_vector[index] * self.speed.value)

        # Interpolate values
        self.position.next(ratio = self.fix_due_fps(self.cfg["walk_responsiveness"]))
        self.speed.next(ratio = self.fix_due_fps(self.cfg["walk_responsiveness"]))
        self.fov.next(ratio = self.fix_due_fps(self.cfg["zoom_responsiveness"]))

        # Apply roll
        if self.want_to_roll != 0:
            self.apply_rotation(self.want_to_roll, Camera3D.AxisX)
            self.want_to_roll = 0

        # For ModeGlobal cancel roll relative to the camera, get angle between XY plane basically
        if self.mode == Camera3D.ModeGlobal:
            a = (math.pi / 2) - angle_between(self.standard_base[2], Camera3D.GlobalZ)
            self.apply_rotation(a/2, Camera3D.AxisX)

        # Apply interpolation to target rotation, normalize current quaternion just in case
        self.do_slerp()
        self.quaternion = np.normalized(self.quaternion)
        
    def key_event(self, key, action, modifiers):
        dpfx = "[Camera3D.key_event]"

        # Walk, rotation
        if action in [0, 1]:
            if (key == 87):  self.want_to_walk_unit_vector[0] =  action  # W
            if (key == 65):  self.want_to_walk_unit_vector[2] = -action  # A
            if (key == 83):  self.want_to_walk_unit_vector[0] = -action  # S 
            if (key == 68):  self.want_to_walk_unit_vector[2] =  action  # D
            if (key == 32):  self.want_to_walk_unit_vector[1] =  action  # Space
            if (key == 340): self.want_to_walk_unit_vector[1] = -action  # Shift
            if (key == 81):  self.want_to_roll = -self.fix_due_fps(action / 200)  # q
            if (key == 69):  self.want_to_roll =  self.fix_due_fps(action / 200)  # e
        
        if (key == 77) and (action == 1):
            self.messages.add(f"{dpfx} (m) Cycle modes", self.ACTION_MESSAGE_TIMEOUT * 4)
            self.cycle_mode()

        if (key == 66) and (action == 1):
            self.messages.add(f"{dpfx} (b) Reset roll to [0°]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_quaternion.x = 0

        if (key == 86) and (action == 1):
            self.messages.add(f"{dpfx} (v) Reset inclination to [90°]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_quaternion.y = 0
            
        if (key == 67) and (action == 1):
            self.messages.add(f"{dpfx} (c) Reset azimuth to [0°]", self.ACTION_MESSAGE_TIMEOUT)
            self.target_quaternion.z = 0

        if (key == 88) and (action == 1):
            self.messages.add(f"{dpfx} (x) Reset camera to (0, 0, 0)", self.ACTION_MESSAGE_TIMEOUT)
            self.position.set_target(np.array([0.0, 0.0, 0.0], dtype = np.float32))

        if (key == 90) and (action == 1):
            self.messages.add(f"{dpfx} (z) Reset FOV to [1x]", self.ACTION_MESSAGE_TIMEOUT)
            self.fov.set_target(1)

    def mouse_drag_event(self, x, y, dx, dy):
        if self.SombreroContext.ctrl_pressed: self.fov += (dy * 0.05) * self.fov.value
        if self.SombreroContext.alt_pressed: self.apply_rotation( self.fix_due_fps(dy/800), Camera3D.AxisX)

    def gui(self):
        imgui.separator()
        imgui.text_colored("Camera 3D", 0, 1, 0)
        cp = self.pointing
        imgui.text(f"Mode: [{self.mode}]")
        imgui.text(f"Camera Pointing:   [{cp[0]:.2f}, {cp[1]:.2f}, {cp[2]:.2f}]")
        imgui.text(f"Quaternion: [{self.quaternion.w:.3f}, {self.quaternion.x:.3f}, {self.quaternion.y:.3f}, {self.quaternion.z:.3f}]")
        imgui.text(f"Position:   [{self.position.value[0]:.3f}, {self.position.value[1]:.3f}, {self.position.value[2]:.3f}]")
        imgui.text(f"Walk speed: [{self.speed.value:.3f}]")
        imgui.text(f"Roll: [{self.roll.value:.3f}]")

    def mouse_scroll_event(self, x_offset, y_offset):
        if self.SombreroContext.alt_pressed: self.fov -= (y_offset * 0.05) * self.fov.value
        elif self.SombreroContext.ctrl_pressed: self.cfg["mouse_sensitivity"] += (y_offset * 0.05) * self.cfg["mouse_sensitivity"]
        else: self.speed += (y_offset * 0.05) * self.speed.value

    def mouse_position_event(self, x, y, dx, dy):
        self.apply_rotation((-dx/500) * self.fov.value, Camera3D.AxisY)
        self.apply_rotation((-dy/500) * self.fov.value, Camera3D.AxisZ)
    
