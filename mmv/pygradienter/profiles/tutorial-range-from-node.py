import sys
sys.path.append("..")

from mmv.pygradienter.linearalgebra import LinearAlgebra, Point
from mmv.pygradienter.node import PointNode
import random
import math
import os


description = "Demonstration on only applying colors within the range of a node"


class PyGradienterProfile():
    def __init__(self, config):
        self.config = config

        self.width = self.config["width"]
        self.height = self.config["height"]

        self.la = LinearAlgebra()
        self.id = 0

        self.name = os.path.basename(__file__).replace(".py", "")
        print("Starting PyGradienterProfile with name [%s]" % self.name)

    def generate_nodes(self):

        # Create N random nodes on the image
        for _ in range(4):
    
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
    
    def pixel_color_transformations(self, rgb, x, y, distances):

        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        a = rgb[3]

        # Make changes on r, g, b

        #

        return [r, g, b, a]

    def get_pixel_by_distances_and_nodes(self, distances, nodes):
        
        this_pixel = [0, 0, 0, 255]

        minimum_distance = min(distances)

        if minimum_distance < 50:
            this_pixel[0] = 255
        
        if minimum_distance < 100:
            this_pixel[1] = 255
        
        if minimum_distance < 200:
            this_pixel[2] = 255

        return this_pixel

