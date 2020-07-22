import sys
sys.path.append("..")

from mmv.pygradienter.linearalgebra import LinearAlgebra, Point
from mmv.pygradienter.node import PointNode
import random
import math
import os


description = "This is a template file, copy and rename to make your own!!"

# This is a class with pre-defined function names that will be called to generate a image
class PyGradienterProfileTemplate():
    def __init__(self, config):
        self.config = config

        # Get some basic info
        self.width = self.config["width"]
        self.height = self.config["height"]

        # Build a LinearAlgebra object
        self.la = LinearAlgebra()
        self.id = 0

        self.name = os.path.basename(__file__).replace(".py", "")
        print("Starting PyGradienterProfile with name [%s]" % self.name)

    def generate_nodes(self):

        # Create N random nodes on the image
        for _ in range(2):
    
            # Create a random Node object with our input
            next_node = PointNode(
                # Position
                [
                    random.randint(0, self.config["width"]),
                    random.randint(0, self.config["height"]),
                ],
                [
                    # Pixel color based on the minimum and maximum pixel colors for each channel
                    random.randint(
                        0,
                        255
                    ),
                    random.randint(
                        0,
                        255
                    ),
                    random.randint(
                        0,
                        255
                    ),
                    255
                ],
                1
            ) 
            
            yield next_node

    # Calculate this point's distance to that node
    def calculate_distance_between_nodes(self, point, node):
        x = point[0]
        y = point[1]

        # Make changes on X and Y

        #

        point = Point(
            [
                x,
                y
            ]
        )
        return self.la.distance(point, node)
    
    # On the final pixel, apply this transformation
    def pixel_color_transformations(self, rgb, x, y, distances):

        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        a = rgb[3]

        # Make changes on r, g, b

        #

        return [r, g, b, a]

    # Here you bias the colors based on the distance to a node and its colors
    # This default one multiplies the distance to a node and its colors
    # then divides this "biased" list by the sum of the distances for a
    # averaged distance - color final pixel
    def get_pixel_by_distances_and_nodes(self, distances, nodes):
        
        # Start with a black pixel
        this_pixel = [0, 0, 0, 0]

        # For each (ordered) distance
        for node_index, distance in enumerate(distances):
            # For each color
            for c in range(4):
                # This color is the distance multiplied by that color node's color
                this_pixel[c] += distance * nodes[node_index].color[c] * nodes[node_index].intensity
        
        # Divide by sum(distances) to calculate the final bias
        this_pixel = [x / sum(distances) for x in this_pixel]

        return this_pixel
