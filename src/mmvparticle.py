"""
===============================================================================

Purpose: MMVParticle object

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


class MMVParticle():
    def __init__(self, context):
        
        debug_prefix = "[MMVParticle.__init__]"
        
        self.context = context

        self.interpolation = Interpolation()
        self.utils = Utils()

        self.path = {}

        self.x = 0
        self.y = 0
        self.size = 1
        self.current_animation = 0
        self.current_step = 0

        # Create Frame and load random particle
        self.frame = Frame()
        self.frame.load_from_path_wait(
            self.utils.random_file_from_dir(
                self.context.assets + os.path.sep + "particles"
            )
        )
    
    # Next step of animation
    def next(self):

        # Animation has ended, this current_animation isn't present on path.keys
        if not self.current_animation in list(self.path.keys()):
            print("No more animations, quitting")
            return

        # The animation we're currently playing
        this_animation = self.path[self.current_animation]
        
        # The current step is one above the steps we've been told, next animation
        if self.current_step == this_animation["steps"] + 1:
            print("Out of steps, next animation")
            self.current_animation += 1
            self.current_step = 0
            return

        # Get info on the animation dic items to operate
        position = this_animation["position"]
        steps = this_animation["steps"]

        # Move according to a Point (be stationary)
        if self.utils.is_matching_type([position], [Point]):

            print("Path is Point, current steps", self.current_step)

            # Atribute (x, y) to Point's x and y
            self.x = position.x
            self.y = position.y

            # Debug
            print("x=", self.x)
            print("y=", self.y)
        
        # Move according to a Line (interpolate current steps)
        if self.utils.is_matching_type([position], [Line]):

            print("Path is Line, current steps", self.current_step, "- interpolating")
            
            start_coordinate = position.start
            end_coordinate = position.end
            
            # Interpolate X coordinate on line
            self.x = self.interpolation.linear(
                start_coordinate[0],  
                end_coordinate[0],
                self.current_step,
                steps
            )

            # Interpolate Y coordinate on line
            self.y = self.interpolation.linear(
                start_coordinate[1],  
                end_coordinate[1],
                self.current_step,
                steps
            )

            print("x=", self.x)
            print("y=", self.y)

        # Next step, end of loop
        self.current_step += 1
            