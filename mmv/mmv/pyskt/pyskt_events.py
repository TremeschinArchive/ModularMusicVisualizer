"""
===============================================================================

Purpose: Events (mouse, keyboard) for a GLFW window

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

import glfw

class PysktEvents:
    def __init__(self, pyskt_main):
        self.pyskt_main = pyskt_main

        # # Mouse

        self.left_click = False
        self.right_click = False
        self.middle_click = False

        # If your mouse has the left side buttons
        self.side_front = False
        self.side_back = False

        # -1 is down, 1 is up
        self.scroll = 0

        # # Keyboard
        
        self.keys_state = {}

        # Paths

        self.drag_n_drop = []

    def reset_non_ending_states(self):
        self.scroll = 0
        self.drag_n_drop = []
        
    def mouse_callback(self, *events):
        # Mouse click
        # events = (<glfw.LP__GLFWwindow>, 0, 0, 0)
        if len(events) == 4:
            state = bool(events[2])
            button = events[1] # 0 - left, 1 - right
            if state:
                print(f"Mouse button {button} clicked")
            else:
                print(f"Mouse button {button} released")
            
            if button == 0:
                self.left_click = state
            elif button == 1:
                self.right_click = state
            elif button == 2:
                self.middle_click = state
            elif button == 3:
                self.side_front = state
            elif button == 4:
                self.side_back = state
                

        # Scroll
        # events = (<glfw.LP__GLFWwindow>, 0.0, 1.0)
        if len(events) == 3:
            if events[2] == 1:
                direction = "up"
            elif events[2] == -1:
                direction = "down"

            print(f"Mouse scroll {direction}")

            self.scroll = events[2]

    # Window has been resized, TODO: resize canvas.. how?
    def on_window_resize(self, window, new_width, new_height):
        print("Window resize,", new_width, new_height)
        self.pyskt_main.pyskt_context.width = new_width
        self.pyskt_main.pyskt_context.width = new_height 

    # If user drops one or multiple files on the window
    def on_file_drop(self, *events):
        paths = events[1]
        self.drag_n_drop = paths
        print(f"Get drag and dropped paths: {paths=}")

    # (<glfw.LP__GLFWwindow>, 51, 12, 0, 0)
    def keyboard_callback(self, *events):
        print(events)
        print(glfw.get_key_name(events[1], events[4]))