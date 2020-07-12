"""
===============================================================================

Purpose: Modifiers (paths, effects, constants) we use under animations
Yes dataclasses would be better but welp

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

from mmv.utils import Utils
from mmv.frame import Frame
import random
import math
import os


# # Paths

# Basic

class Line():
    # @start, end: 2d coordinate list [0, 2]
    def __init__(self, start, end):
        self.start = start
        self.end = end

class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Linear Algebra / "Physics" / motion?

class VelocityVector():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Shake():
    # @config: dict
    #    @"interpolation_$": Interpolation function on that $ axis
    #    @"arg_$": Interpolation argument letter $, see Interpolation class
    #    @"$_steps": How much steps to end interpolation
    #    @"distance": Max shake distance in any square direction
    #    
    def __init__(self, config):

        # Get config
        self.interpolation_x = config["interpolation_x"]
        self.interpolation_y = config["interpolation_y"]
        self.distance = config["distance"]
        self.x_steps = config["x_steps"]
        self.y_steps = config["y_steps"]
        self.arg_a = config["arg_a"]
        self.arg_b = config["arg_b"]

        # Start at the center point
        self.x = 0
        self.y = 0

        # Where we're going to interpolate next
        self.towards_x = 0
        self.towards_y = 0

        # Count of steps on each axis
        self.current_x_step = 0
        self.current_y_step = 0

        # Get a next random point as we're starting on (0, 0)
        self.next_random_point("both")
    
    # Generate a next random coordinate to shake to according to the max distance
    # @who: "x", "y" or "both"
    def next_random_point(self, who):
        if who == "x":
            self.towards_x = random.randint(-self.distance, self.distance)
        elif who == "y":
            self.towards_y = random.randint(-self.distance, self.distance)
        elif who == "both":
            self.next_random_point("x")
            self.next_random_point("y")
    
    # Next step of this X and Y towards the current random point
    # @who: "x", "y" or "both"
    def next(self, who="both"):
        
        if who == "both":
            self.next("x")
            self.next("y")

        # X axis
        if who == "x":

            if isinstance(self.current_x_step, int):
                self.current_x_step += 1

            if self.x_steps == "end_interpolation":
                # If X is within two pixels of the target, end interpolation
                if abs(self.x - self.towards_x) < 2:
                    self.x = self.towards_x
                    self.next_random_point("x")
                    self.current_x_step = 0
                    return
            else:
                if self.current_x_step == self.x_steps + 1:
                    self.next_random_point("x")
                    self.current_x_step = 0
                    return

            # Calculate next interpolation
            self.x = round(
                self.interpolation_x(
                    self.x,
                    self.towards_x,
                    self.current_x_step,
                    self.x_steps,
                    self.x,
                    self.arg_a,
                    self.arg_b
                ),
                2
            )

        # Y axis
        if who == "y":
            
            if isinstance(self.current_y_step, int):
                self.current_y_step += 1

            if self.y_steps == "end_interpolation":
                # If Y is within two pixels of the target, end interpolation
                if abs(self.y - self.towards_y) < 2:
                    self.y = self.towards_y
                    self.next_random_point("y")
                    self.current_y_step = 0
                    return
            else:
                if self.current_y_step == self.y_steps + 1:
                    self.next_random_point("y")
                    self.current_y_step = 0
                    return

            # Calculate next interpolation
            self.y = round(
                self.interpolation_y(
                    self.y,
                    self.towards_y,
                    self.current_y_step,
                    self.y_steps,
                    self.y,
                    self.arg_a,
                    self.arg_b
                ),
                2
            )

# Swing back and forth in the lines of a sine wave
class SineSwing():
    # @max_value: Maximum amplitute of the sine wave
    # @smooth: Add this part of 1 (1/smooth) on each next step to current X
    def __init__(self, max_value, smooth):
        self.smooth = smooth
        self.max_value = max_value
        self.x = 0
    
    # Return next value of the iteration
    def next(self):
        self.x += 1 / self.smooth
        return self.max_value * math.sin(self.x)


# Swing to one direction
class LinearSwing():
    # @smooth: Add this part of 1 (1/smooth) on each next step to current X
    def __init__(self, smooth):
        self.smooth = smooth
        self.x = 0
    
    # Return next value of the iteration
    def next(self):
        self.x += 1 / self.smooth
        return self.x

# # Values

class Constant():
    def __init__(self, value):
        self.value = value

# # Effects

class Fade():
    # @start_percentage, end_percentage: Ranges from 0 to 1, 0 being transparent and 1 opaque
    # @finish_steps: In how many steps to finish the fade
    def __init__(self, start_percentage, end_percentage, finish_steps):
        self.start_percentage = start_percentage
        self.end_percentage = end_percentage
        self.finish_steps = finish_steps
        self.current_step = 0