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
import copy
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

        # Base offset is the default offset when calling .next at the end
        # Offset is the animations and motions this frame offset
        self.base_offset = [0, 0]
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
        
        # Reset offset
        self.offset = [0, 0]

        positions = this_animation["position"]
        steps = this_animation["steps"]

        if "modules" in this_animation:
            
            modules = this_animation["modules"]

            if "rotate" in modules:
                rotate = modules["rotate"]["object"]
                self.image.rotate(rotate.next())

            if "resize" in modules:
        
                a = fftinfo["average_value"]

                if a > 1:
                    a = 1
                if a < -0.9:
                    a = -0.9

                a = modules["resize"]["interpolation"](
                    self.size,
                    eval(modules["resize"]["activation"].replace("X", str(a))),
                    self.current_step,
                    steps,
                    self.size,
                    modules["resize"]["arg_a"]
                )
                self.size = a

                offset = self.image.resize_by_ratio(
                    a,
                    # If we're going to rotate, resize the rotated frame which is not the original image
                    from_current_frame="rotate" in modules
                )

                if modules["resize"]["keep_center"]:
                    self.offset[0] += offset[0]
                    self.offset[1] += offset[1]

            if "blur" in modules:
                self.image.gaussian_blur(
                    eval(modules["blur"]["activation"].replace("X", str(fftinfo["average_value"])))
                )
            
            if "fade" in modules:
                
                fade = modules["fade"]["object"]
                
                if fade.current_step < fade.finish_steps:
                    t = modules["fade"]["interpolation"](
                        fade.start_percentage,  
                        fade.end_percentage,
                        self.current_step,
                        fade.finish_steps,
                        fade.current_step,
                        modules["fade"]["arg_a"]
                    )
                    self.image.transparency(t)
                    fade.current_step += 1
                else:
                    # TODO: Failsafe really necessary?
                    self.image.transparency(fade.end_percentage)
            
            # print("APP", a)

        # Iterate through every position module
        for position in positions:
            
            # # Override modules

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

                # Interpolate X coordinate on line
                self.x = this_animation["interpolation_x"](
                    start_coordinate[1],  
                    end_coordinate[1],
                    self.current_step,
                    steps,
                    self.x,
                    this_animation["interpolation_x_arg_a"]
                )

                # Interpolate Y coordinate on line
                self.y = this_animation["interpolation_y"](
                    start_coordinate[0],  
                    end_coordinate[0],
                    self.current_step,
                    steps,
                    self.y,
                    this_animation["interpolation_y_arg_a"]
                )
            
            # # Offset modules

            # Get next shake offset value
            if self.utils.is_matching_type([position], [Shake]):
                position.next()
                self.offset[0] += position.x
                self.offset[1] += position.y

        # Next step, end of loop
        self.current_step += 1
    
    # Blit this item on the canvas
    def blit(self, canvas):

        img = self.image
        width, height, _ = img.frame.shape
        
        # print("OFFSET:", self.offset)

        x = int(self.x + self.offset[1] + self.base_offset[1])
        y = int(self.y + self.offset[0] + self.base_offset[0])


        if True:
            # This is the right way but it's slow TODO: R&D
            canvas.canvas.overlay_transparent(
                self.image.frame,
                y,
                x
            )

        if False:
            # This is the right way but it's slow TODO: R&D
            canvas.canvas.overlay_transparent(
                self.image.frame,
                x,
                y
            )

        if False:
            # Fast but ugly
            canvas.canvas.copy_from(
                self.image.frame,
                canvas.canvas.frame,
                [0, 0],
                [x, y],
                [x + width - 1, y + height - 1]
            )
