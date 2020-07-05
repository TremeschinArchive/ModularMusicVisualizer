"""
===============================================================================

Purpose: MMVImage object

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

from interpolation import Interpolation
from modifiers import *
from frame import Frame
from utils import Utils
import os


class MMVImage():
    def __init__(self, context):
        
        debug_prefix = "[MMVImage.__init__]"
        
        self.context = context

        self.interpolation = Interpolation()
        self.utils = Utils()

        self.path = {}

        self.x = 0
        self.y = 0
        self.size = 1
        self.current_animation = 0
        self.current_step = 0
        self.is_deletable = False
        self.offset = [0, 0]

        # Create Frame and load random particle
        self.image = Frame()
        
    # Next step of animation
    def next(self, fftinfo):

        # Animation has ended, this current_animation isn't present on path.keys
        if not self.current_animation in list(self.path.keys()):
            # print("No more animations, quitting")
            self.is_deletable = True
            return

        # The animation we're currently playing
        this_animation = self.path[self.current_animation]
        
        # The current step is one above the steps we've been told, next animation
        if self.current_step == this_animation["steps"] + 1:
            # print("Out of steps, next animation")
            self.current_animation += 1
            self.current_step = 0
            return

        # Get info on the animation dic items to operate
        interpolation_x = this_animation["interpolation_x"]
        interpolation_y = this_animation["interpolation_y"]
        
        interpolation_x_arg_a = None
        if "interpolation_x_arg_a" in this_animation:
            interpolation_x_arg_a = this_animation["interpolation_x_arg_a"]
        
        interpolation_y_arg_a = None
        if "interpolation_y_arg_a" in this_animation:
            interpolation_y_arg_a = this_animation["interpolation_y_arg_a"]

        position = this_animation["position"]
        steps = this_animation["steps"]

        if "testlink" in this_animation:
            a = fftinfo["average_value"]
            if a > 1:
                a = 1
            if a < -0.9:
                a = -0.9

            a = self.interpolation.remaining_approach(
                self.size,
                1 + 3*a,
                self.current_step,
                steps,
                self.size,
                0.2
            )

            # print("APP", a)
            self.size = a
            self.offset = self.image.resize_by_ratio(a)

        # Move according to a Point (be stationary)
        if self.utils.is_matching_type([position], [Point]):
            # Atribute (x, y) to Point's x and y
            self.x = int(position.y)
            self.y = int(position.x)

        # Move according to a Line (interpolate current steps)
        if self.utils.is_matching_type([position], [Line]):

            # Where we start and end
            start_coordinate = position.start
            end_coordinate = position.end

            if interpolation_x == "sigmoid":
                interpolation_x_function = self.interpolation.sigmoid
            if interpolation_x == "linear":
                interpolation_x_function = self.interpolation.linear
            if interpolation_x == "remaining_approach":
                interpolation_x_function = self.interpolation.remaining_approach

            if interpolation_y == "sigmoid":
                interpolation_y_function = self.interpolation.sigmoid
            if interpolation_y == "linear":
                interpolation_y_function = self.interpolation.linear
            if interpolation_y == "remaining_approach":
                interpolation_y_function = self.interpolation.remaining_approach
            
            # Interpolate X coordinate on line
            self.x = interpolation_x_function(
                start_coordinate[1],  
                end_coordinate[1],
                self.current_step,
                steps,
                self.x,
                interpolation_x_arg_a
            )

            # Interpolate Y coordinate on line
            self.y = interpolation_y_function(
                start_coordinate[0],  
                end_coordinate[0],
                self.current_step,
                steps,
                self.y,
                interpolation_y_arg_a
            )

        # Next step, end of loop
        self.current_step += 1
    
    # Blit this item on the canvas
    def blit(self, canvas):

        img = self.image
        width, height, _ = img.frame.shape
        
        # print("OFFSET:", self.offset)

        x = int(self.x + self.offset[1])
        y = int(self.y + self.offset[0])

        if False:
            # This is the right way but it's slow TODO: R&D
            canvas.canvas.overlay_transparent(
                self.image.frame,
                x,
                y
            )
        else:
            # Fast but ugly
            canvas.canvas.copy_from(
                self.image.frame,
                canvas.canvas.frame,
                [0, 0],
                [x, y],
                [x + width - 1, y + height - 1]
            )
