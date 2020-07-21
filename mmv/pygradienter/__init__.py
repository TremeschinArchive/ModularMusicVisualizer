"""
===============================================================================

Purpose: Module class to interact with PyGradienter

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

from pygradienter.processing import PyGradienterProcessing
from pygradienter.main import PyGradienterMain
from pygradienter.utils import Miscellaneous
from pygradienter.utils import Utils
from multiprocessing import Pool
import copy
import sys
import os


# Unclutter PyGradienterMain class
class Config:
    def __init__(self, pygradientermain):
        self.pygradienter = pygradienter
    
    def n_images(self, n):
        self.pygradienter.n_images = n
    
    def width(self, width):
        self.pygradienter.width = width

    def height(self, height):
        self.pygradienter.height = height
    
    def resolution(self, width, height):
        self.width(width)
        self.height(height)

    def quiet(self, value=True):
        self.pygradienter.quiet = value
    
    def advanced(self, dictionary):
        self.n_images(dictionary["n_images"])
        self.width(dictionary["width"])
        self.height(dictionary["height"])
        self.quiet(dictionary["quiet"])


# Main class that controls PyGradienter
class pygradienter():
   
    def __init__(self):

        # Create Utils and get this file location
        self.utils = Utils()
        self.config = Config(self)
        self.main = PyGradienterMain()

        # Default values
        self.n_images = 1
        self.width = 200
        self.height = 200
        self.show_welcome_message = True
        self.quiet = False

    def generate(self):
        return self.main.generate()
