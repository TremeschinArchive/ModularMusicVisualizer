import sys
sys.path.append("..")

from mmv.pygradienter.linearalgebra import LinearAlgebra, Point
from mmv.pygradienter.node import PointNode
from mmv.pygradienter.noise import Noise

import random
import math
import os


description = "A somewhat fabric looking like texture"


class PyGradienterProfileFabric():
    def __init__(self, config):
        self.config = config

        self.width = self.config["width"]
        self.height = self.config["height"]

        self.la = LinearAlgebra()
        self.id = 0

        self.name = os.path.basename(__file__).replace(".py", "")
        print("Starting PyGradienterProfileFabric with name [%s]" % self.name)

    def generate_nodes(self):

        random.seed(self.id)

        min_stretch = 10
        max_stretch = 20
    
        self.noise_red = Noise()
        self.noise_red.new_simplex(
            random.randint(min_stretch, max_stretch),
            random.randint(min_stretch, max_stretch),
            self.id + 1
        )

        self.noise_green = Noise()
        self.noise_green.new_simplex(
            random.randint(min_stretch, max_stretch),
            random.randint(min_stretch, max_stretch),
            self.id + 2
        )

        self.noise_blue = Noise()
        self.noise_blue.new_simplex(
            random.randint(min_stretch, max_stretch),
            random.randint(min_stretch, max_stretch),
            self.id + 3
        )

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

    def calculate_distance_between_nodes(self, point, node):
        x = point[0]
        y = point[1]

        # Make changes on X and Y

        x = x*math.sin(x/2)**4
        y = y*math.cos(y/2)**4

        y += math.sin(x)*20

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

        # Apply some shading to black
        r *= math.sin((x+(self.noise_red.get_simplex2d(x, y)*10))/self.width)*0.5 + math.cos(y/self.height)*0.5
        g *= math.sin((x+(self.noise_green.get_simplex2d(x, y)*10))/self.width)*0.5 + math.cos(y/self.height)*0.5
        b *= math.sin((x+(self.noise_blue.get_simplex2d(x, y)*10))/self.width)*0.5 + math.cos(y/self.height)*0.5

        r += self.noise_red.get_simplex2d(x, y)*2
        g += self.noise_green.get_simplex2d(x, y)*2
        b += self.noise_blue.get_simplex2d(x, y)*2

        return [r, g, b, a]

    def get_pixel_by_distances_and_nodes(self, distances, nodes):
        
        this_pixel = [0, 0, 0, 0]

        for node_index, distance in enumerate(distances):
            for c in range(4):
                this_pixel[c] += distance * nodes[node_index].color[c] * nodes[node_index].intensity
        
        sum_distances = sum(distances)

        this_pixel = [x / sum_distances for x in this_pixel]

        return this_pixel