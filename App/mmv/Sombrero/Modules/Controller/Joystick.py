"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Joysticks module that detect on the go devices and make it possible
to control the camera or other stuff based on context.live_mode

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
import imgui
import pygame
from mmv.Sombrero.modules.base_module import BaseModule
from mmv.Sombrero.sombrero_context import RealTimeModes


class Joysticks(BaseModule):
    def __init__(self, sombrero_window):
        self.init(sombrero_window)
        pygame.init()
        pygame.joystick.init()

        self.events = []
        self.axis = {i: 0 for i in range(6)}
        self.hat = (0, 0)
        self.buttons = []
        self.joysticks = []
        self.ready = False

    def update_joysticks(self):
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    def next(self):
        dpfx = "[Joysticks.next]"
        self.ready = len(self.joysticks) > 0

        for event in pygame.event.get():
            self.update_joysticks()
            self.events.append(event)

            # Add specific button events
            if event.type == pygame.JOYAXISMOTION: self.axis[event.axis] = event.value
            if event.type == pygame.JOYHATMOTION:  self.hat = event.value
            if event.type == pygame.JOYBUTTONDOWN: self.buttons.append(event.button)
            if event.type == pygame.JOYBUTTONUP:   self.buttons = [x for x in self.buttons if not x == event.button]
            if event.type in [pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED]: pass

            # Select button toggle context modes
            if (event.type == pygame.JOYBUTTONDOWN) and (event.button == 6):
                self.context.live_mode = RealTimeModes.cycle_mode(self.context.live_mode)
                self.context.window_show_menu = False

            # Right axis press, cycle camera 3d mode
            if (event.type == pygame.JOYBUTTONDOWN) and (event.button == 10):
                self.messages.add(f"{dpfx} ", self.ACTION_MESSAGE_TIMEOUT)
                self.context.camera3d.cycle_mode()

        if self.ready:
            c2d = self.context.camera2d
            c3d = self.context.camera3d

            # Joystick -> Camera2D
            if self.context.live_mode == RealTimeModes.Mode2D:
                c2d.apply_rotated_drag(0, 3*self.axis[1], inverse = True)
                c2d.apply_rotated_drag(3*self.axis[0], 0, inverse = True)
                c2d.zoom += (self.axis[4] / 100) * c2d.zoom.value
                c2d.rotation += (self.axis[3] / 100)

            # Joystick -> Camera3D
            if self.context.live_mode == RealTimeModes.Mode3D:
                c3d.want_to_walk_unit_vector[0] = -self.axis[1]
                c3d.want_to_walk_unit_vector[2] =  self.axis[0]
                c3d.want_to_walk_unit_vector[1] =  ((self.axis[5] + 1) / 2) - ((self.axis[2] + 1) / 2)
                c3d.mouse_position_event(0, 0, c3d.sensitivity.value * 10 * self.axis[3], 0)
                c3d.mouse_position_event(0, 0, 0, c3d.sensitivity.value * 10 * self.axis[4])
                if 4 in self.buttons: c3d.want_to_roll = self.context._fix_ratio_due_fps(-1 / 200)
                if 5 in self.buttons: c3d.want_to_roll = self.context._fix_ratio_due_fps( 1 / 200)

    def gui(self):
        imgui.separator()
        if len(self.joysticks) == 0:
            imgui.text_colored("No Joysticks connected.", 1, 0, 0)
        else:
            imgui.text_colored("Joysticks:", 0, 1, 0)
            for index, item in enumerate(self.joysticks):
                imgui.text(f" - [{index}]: [{item.get_name()}]")
            ax = "Axis:"
            for index, value in self.axis.items():
                ax += f" [{index}: {value:.1f}]"
            imgui.text(ax)
            imgui.text(f"Buttons: [{' '.join([str(x) for x in self.buttons])}]")
