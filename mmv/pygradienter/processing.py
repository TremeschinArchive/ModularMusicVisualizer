"""
===============================================================================

Purpose: Produce a gradient image based on a set of nodes

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

from mmv.common.utils import Utils
from PIL import ImageFilter
from PIL import Image
import numpy as np
import datetime
import random
import math
import time
import sys
import os


# Controller routine / class that uses the profile Python script to get values
class PyGradienterProcessing():
    def __init__(self, profile):

        # Load the profile and a config
        self.profile = profile
        self.config = profile.config

        if not self.config["quiet"]:
            print("Starting generating id [%s]" % self.profile.id)

        # Create classes
        self.utils = Utils()

        # Empty / "static" variables
        # self.unique_string = ""
        self.nodes = []
        self.ROOT = self.utils.get_root()

        # Where we'll save
        savefolder = self.ROOT + os.path.sep + "data" + os.path.sep + self.profile.name + os.path.sep + "%sx%s" % (self.config["width"], self.config["height"])
        self.utils.mkdir_dne(savefolder)

        # Create a empty canvas
        self.new_canvas()

        # Add profile nodes
        for node in self.profile.generate_nodes():
            self.nodes.append(node)
        
        # Main routine, generate the image
        self.generate()

        # Save
        # self.save(savefolder + os.path.sep + self.utils.get_hash(self.unique_string) + ".png")
        self.save(savefolder + os.path.sep + self.utils.get_hash(datetime.datetime.now().strftime("%d%m%Y-%H:%M:%S") + "_" + str(self.profile.id)) + ".png")

        # Clean canvas as multiprocessing doesn't destroy the object on memory?
        self.canvas = None

    # Create a black canvas as a list and starting image
    def new_canvas(self):
        self.canvas = np.zeros([self.config["height"], self.config["width"], 4], dtype=np.uint8)    

        # Set alpha channel to 255
        for i, _ in enumerate(self.canvas):
            for j, _ in enumerate(self.canvas[i]):
                self.canvas[i][j][3] = 255
    
    # Replace "width" with self.config["width"] and "height" with self.config["height"] on the setting
    def pos_replace(self, s):
        return str(s).replace("width", str(self.config["width"])).replace("height", str(self.config["height"]))

    # Main routine on making the images
    def generate(self):

        # Loop through the image X and Y pixels
        for y in range(self.config["height"]):
            for x in range(self.config["width"]):
                
                # The sum of the distances                 
                distances = np.zeros(len(self.nodes))

                # The actual pixel we'll be setting the color to
                this_pixel = np.array([0, 0, 0])

                # For each node, calculate its distance
                for i, node in enumerate(self.nodes):

                    # Calculate the raw distance between two nodes
                    distance = self.profile.calculate_distance_between_nodes (
                        [x, y],
                        node.la
                    )

                    # Add to the total sum
                    distances[i] = distance

                    # If there is only one node or the distance is zero to a note, set it to the node color
                    if distances[-1] == 0:
                        this_pixel = list(node.color)
                    
                # Loop through the colors

                # If the pixel is not inside a node
                if not 0 in distances:
                    this_pixel = self.profile.get_pixel_by_distances_and_nodes(distances, self.nodes)

                # Generate (hopefully) a unique string to save the images
                # self.unique_string += str(distances[-1] * this_pixel[0] * this_pixel[1] * this_pixel[2] * time.time())[0:1]
                
                # Change and activate the pixel colors by their value
                self.canvas[y][x] = self.profile.pixel_color_transformations(this_pixel, x, y, distances)

    # Save an image to disk                
    def save(self, path):

        if not self.config["quiet"]:
            print("Save id [%s]" % self.profile.id)

        # Get a image from the numpy array, smooth it a bit and save
        img = Image.fromarray(self.canvas, mode="RGBA")
        img = img.filter(ImageFilter.SMOOTH)
        img.save(path, quality=95)
