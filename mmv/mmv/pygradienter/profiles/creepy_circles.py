import sys
sys.path.append("..")

from mmv.common.cmn_linearalgebra import LinearAlgebra
from mmv.pygradienter.pyg_node import LAPointNode
from mmv.common.cmn_linearalgebra import LAPoint
import random
import math
import os


description = "(5/10 disturbing) Creepy shady circles"


class PyGradienterProfileCreepyCircles():
    def __init__(self, config):
        self.config = config

        self.width = self.config["width"]
        self.height = self.config["height"]
        self.diagonal = (self.width**2 + self.height**2)**0.5

        self.la = LinearAlgebra()
        self.id = 0

        self.name = os.path.basename(__file__).replace(".py", "")
        print("Starting PyGradienterProfileCreepyCircles with name [%s]" % self.name)

    def generate_nodes(self):

        random.seed(self.id)

        if random.randint(1, 2) == 1:
            self.subtract_one_from_darkness_bias = True
        else:
            self.subtract_one_from_darkness_bias = False

        # Create N random nodes on the image
        for _ in range(random.randint(1, 4)):
    
            # Create a random Node object with our input
            next_node = LAPointNode(
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

        mind = min(distances)

        if mind == 0:
            mind = 1

        r = (255*((math.sin((mind/20)))/2 + 0.5))
        g = (255*((math.sin((mind/20) + 2*math.pi/3))/2 + 0.5))
        b = (255*((math.sin((mind/20) + 4*math.pi/3))/2 + 0.5))

        darkness_bias = ( mind / (self.diagonal*0.7) )

        if self.subtract_one_from_darkness_bias:
            darkness_bias = 1 - darkness_bias

        if darkness_bias < 0:
            darkness_bias = 0

        r *= darkness_bias
        g *= darkness_bias
        b *= darkness_bias

        #

        return [r, g, b, a]
            
    def get_pixel_by_distances_and_nodes(self, distances, nodes):
            
        this_pixel = [0, 0, 0, 0]

        for node_index, distance in enumerate(distances):
            for c in range(4):
                this_pixel[c] += distance * nodes[node_index].color[c] * nodes[node_index].intensity
        
        sum_distances = sum(distances)

        this_pixel = [x / sum_distances for x in this_pixel]

        return this_pixel