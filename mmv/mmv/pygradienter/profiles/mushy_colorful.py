from mmv.common.cmn_linearalgebra import LinearAlgebra, LAPoint
from mmv.pygradienter.pyg_node import LAPointNode
import random
import math
import os


description = "A mushy colorful but a bit dark texturewith some reflections"


class PyGradienterProfileMushyColorful():
    def __init__(self, width, height):
        self.config = config

        self.width = width
        self.height = height

        self.la = LinearAlgebra()
        self.id = 0

        away = 100

        self.point_a = LAPoint([-away, -away]) # top left
        self.point_b = LAPoint([self.width + away, 0 + away]) # top right
        self.point_c = LAPoint([-away, self.height + away]) # bottom left
        self.point_d = LAPoint([self.width + away, self.height + away]) # bottom right

    def generate_nodes(self):

        close = 0.8

        # Create N random nodes on the image
        for _ in range(2):
    
            # Create a random Node object with our input
            next_node = LAPointNode(
                # Position
                [
                    random.choice(random.choice([
                        range(int(-self.width), int(-close**self.width)),
                        range(int((2-close)*self.width), int(2*self.width))
                    ])),
                    random.choice(random.choice([
                        range(int(-self.height), int(-close*self.height)),
                        range(int((2-close)*self.height), int(2*self.height))
                    ]))
                ],
                [
                    # Pixel color based on the minimum and maximum pixel colors for each channel
                    random.randint(
                        100,
                        255
                    ),
                    random.randint(
                        100,
                        255
                    ),
                    random.randint(
                        100,
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

        r *= math.tanh(math.pi - abs(self.la.angle_between_three_points(
            self.point_a,
            LAPoint([x, y]),
            self.point_b
        )))

        g *= math.tanh(math.pi - abs(self.la.angle_between_three_points(
            self.point_b,
            LAPoint([x, y]),
            self.point_c
        )))

        b *= math.tanh(math.pi - abs(self.la.angle_between_three_points(
            self.point_c,
            LAPoint([x, y]),
            self.point_d
        )))

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