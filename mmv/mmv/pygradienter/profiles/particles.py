import sys
sys.path.append("..")

from mmv.common.cmn_linearalgebra import LinearAlgebra, LAPoint
from mmv.pygradienter.pyg_node import LAPointNode
import random
import math
import os


description = "White star-like particles"


class PyGradienterProfileParticles():
    def __init__(self, width, height):
        self.config = config

        self.width = width
        self.height = height

        self.la = LinearAlgebra()
        self.id = 0

    def generate_nodes(self):

        random.seed(self.id)

        self.random_exponent = random.uniform(0.2, 2.4)
        
        # White note at the center
        next_node = LAPointNode(
            # Position
            [
                width // 2,
                height // 2,
            ],
            [
                # Pixel color based on the minimum and maximum pixel colors for each channel
                255,
                255,
                255,
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

        point = LAPoint(
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

    def proportion(self, a, b, c):
        # a - b
        # c - x
        # x = b*c/a
        return b*c/a
    
    def get_pixel_by_distances_and_nodes(self, distances, nodes):
        
        this_pixel = [255, 255, 255, 0]

        transparent = self.proportion(
            self.width/2,
            1,
            sum(distances)
        )

        transparent = transparent ** self.random_exponent

        transparent *= 255

        if transparent > 255:
            transparent = 255

        this_pixel[3] = 255 - transparent

        return this_pixel
