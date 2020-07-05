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

from utils import Utils
from frame import Frame
import random
import math
import os


# # Paths

# Basic

class Line():
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
    def __init__(self, config):

        # Start at the center point
        self.x = 0
        self.y = 0

        # Where we're going to interpolate next
        self.towards_x = 0
        self.towards_y = 0

        self.current_x_step = 0
        self.current_y_step = 0

        # Get config
        self.interpolation = config["interpolation"]
        self.distance = config["distance"]
        self.x_steps = config["x_steps"]
        self.y_steps = config["y_steps"]
        self.arg_a = config["arg_a"]
        self.arg_b = config["arg_b"]

        self.next_random_point("both")
    
    def next_random_point(self, who):
        if who == "x":
            self.towards_x = random.randint(-self.distance, self.distance)
        elif who == "y":
            self.towards_y = random.randint(-self.distance, self.distance)
        elif who == "both":
            self.next_random_point("x")
            self.next_random_point("y")
    
    def next(self, who="both"):
        
        if who == "both":
            self.next("x")
            self.next("y")

        # X 
        if who == "x":

            if isinstance(self.current_x_step, int):
                self.current_x_step += 1

            if self.x_steps == "end_interpolation":
                # If both X and Y are within two pixels of the target 
                if abs(self.x - self.towards_x) < 2:
                    self.next_random_point("x")
                    self.current_x_step = 0
                    return
            else:
                if self.current_x_step == self.x_steps + 1:
                    self.next_random_point("x")
                    self.current_x_step = 0
                    return

            self.x = round(
                self.interpolation(
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

        # Y
        if who == "y":
            
            if isinstance(self.current_y_step, int):
                self.current_y_step += 1

            if self.y_steps == "end_interpolation":
                if abs(self.y - self.towards_y) < 2:
                    self.next_random_point("y")
                    self.current_y_step = 0
                    return
            else:
                if self.current_y_step == self.y_steps + 1:
                    self.next_random_point("y")
                    self.current_y_step = 0
                    return

            self.y = round(
                self.interpolation(
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


# # Values

class Constant():
    def __init__(self, value):
        self.value = value

# # Effects

class Fade():
    def __init__(self, start_percentage, end_percentage, finish_steps):
        self.start_percentage = start_percentage
        self.end_percentage = end_percentage
        self.finish_steps = finish_steps
        self.current_step = 0