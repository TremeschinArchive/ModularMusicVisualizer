import sys
sys.path.append("..")

from mmv.common.cmn_linearalgebra import LinearAlgebra, LAPoint
from mmv.pygradienter.pyg_node import LAPointNode
import random
import uuid
import os


description = "Simple and clean gradients"


class PyGradienterProfileSimple():
    def __init__(self, width, height):
        self.config = config

        self.width = width
        self.height = height

        self.la = LinearAlgebra()
        self.id = 0

        self.name = os.path.basename(__file__).replace(".py", "")
        print("Starting PyGradienterProfileSimple with name [%s]" % self.name)

    def generate_nodes(self):

        random.seed(uuid.uuid4())

        # Create N random nodes on the image
        for _ in range(2):
    
            # Create a random Node object with our input
            next_node = LAPointNode(
                # Position
                [
                    random.randint(0, width),
                    random.randint(0, height),
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
        point = LAPoint(
            [
                point[0],
                point[1]
            ]
        )
        return self.la.distance(point, node)
    
    def pixel_color_transformations(self, rgb, x, y, distances):

        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        a = rgb[3]

        return [r, g, b, a]
    
    def get_pixel_by_distances_and_nodes(self, distances, nodes):
        
        this_pixel = [0, 0, 0, 0]

        for node_index, distance in enumerate(distances):
            for c in range(4):
                this_pixel[c] += distance * nodes[node_index].color[c] * nodes[node_index].intensity
        
        sum_distances = sum(distances)

        this_pixel = [x / sum_distances for x in this_pixel]

        return this_pixel
