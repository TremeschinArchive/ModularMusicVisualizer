"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Set ups colors based on a few presets and whatnot for the piano roll

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

import random


class PianoRollColorsHelper:
    def __init__(self):
        self.colors = {}
    
    # Set a seed so we get the same result given a random choice
    def seeded(self, n):
        random.seed(n)

    def piano(self, preset, **kwargs):
        if preset == "custom":
            self.colors.update(kwargs)

        if preset == "default":
             self.colors.update({
                "sharp_key_idle_1":    [47, 45, 33, 255],
                "sharp_key_idle_2":    [45, 45, 45, 255],
                "sharp_key_pressed_1": [16, 16, 16, 255],
                "sharp_key_pressed_2": [21, 19, 5, 255],
                "sharp_key_3d_effect": [30, 30, 30, 255],

                "plain_key_idle_1":    [255, 255, 255, 255],
                "plain_key_idle_2":    [255, 250, 211, 255],
                "plain_key_pressed_1": [140, 140, 140, 255],
                "plain_key_pressed_2": [114, 114, 114, 255],
                "plain_key_3d_effect": [187, 187, 187, 255],
                
                "end_piano_shadow": [40, 40, 40, 255],
            })

    def markers(self, preset, **kwargs):
        if preset == "custom":
            self.colors.update(kwargs)

        if preset == "default":
            self.colors.update({
                # "marker_color_sharp_keys": [255, 255, 255, 30],
                "marker_color_sharp_keys": None,
                "marker_color_between_two_white": [255, 255, 255, 30],
                "marker_color_g_sharp": [255, 255, 255, 40],
            })
        
        if preset == "easy":
            self.colors.update({
                # "marker_color_sharp_keys": [255, 255, 255, 30],
                "marker_color_sharp_keys": None,
                "marker_color_between_two_white": [255, 255, 255, 130],
                "marker_color_g_sharp": None,
            })

    
    def set_note_preset(self, channel, preset, custom = {}):
        if preset == "vibrant-red":
            d = {
                "plain_1": [255, 50, 50],
                "plain_2": [168, 45, 45],
                "sharp_1": [153, 50, 50],
                "sharp_2": [181, 46, 5],
                "border_shadow": [153, 50, 50]
            }

        elif preset == "acid-yellow":
            d = {
                "plain_1": [255, 204, 0],
                "plain_2": [130, 255, 136],
                "sharp_1": [255, 157, 0],
                "sharp_2": [99, 255, 107],
                "border_shadow": [255, 157, 0]
            }

        elif preset == "forest-green":
            d = {
                "plain_1": [0, 255, 13],
                "plain_2": [152, 84, 255],
                "sharp_1": [0, 166, 8],
                "sharp_2": [94, 53, 156],
                "border_shadow": [0, 166, 8]
            }
        
        elif preset == "magic-purple":
            d = {
                "plain_1": [102, 0, 255],
                "plain_2": [194, 83, 83],
                "sharp_1": [57, 0, 143],
                "sharp_2": [255, 115, 115],
                "border_shadow": [57, 0, 143]
            }
        
        elif preset == "custom":
            d = custom
        
        else:
            raise RuntimeError(f"Preset not found: [{preset}]")
        
        self.colors.update({
            f"channel_{channel}": d
        })

    def background(self, preset, **kwargs):
        if preset == "custom":
            self.colors.update(kwargs)

        if preset == "default":
            self.colors.update({
                "background_1": [28, 42, 72, 255],
                "background_2": [28, 74, 64, 255],
            })
        
        if preset == "transparent":
            self.colors.update({
                "background_1": [0, 0, 0, 0],
                "background_2": [0, 0, 0, 0],
            })
