"""
===============================================================================

Purpose: Function routines for PySKT like collision checking, proportions

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

import numpy as np
import math
import skia


class PysktProcessing:
    def __init__(self, pyskt_main):
        self.pyskt_main = pyskt_main
    
    # # #

    # https://stackoverflow.com/questions/7261936

    # https://stackoverflow.com/a/63013204/13477696
    def num2col(self, n):
        n, rem = divmod(n - 1, 26)
        next_char = chr(65 + rem)
        if n:
            return self.num2col(n) + next_char
        else:
            return next_char
    
    # https://stackoverflow.com/a/63013204/13477696
    def col2num(self, s):
        n = ord(s[-1]) - 64
        if s[:-1]:
            return 26 * (self.col2num(s[:-1])) + n
        else:
            return n
            
    # # # 

    # Absolute area between two vectors so doesn't matter what direction they are at
    def abs_cross_product(self, V1, V2):
        V1 = np.array(V1)
        V2 = np.array(V2)
        return np.abs(np.cross(V1, V2))
    
    # Get the area of a triangle with three coordinate points
    def three_points_triangle_area(self, P1, P2, P3):

        # Transform the points into an array
        P1, P2, P3 = np.array(P1), np.array(P2), np.array(P3)

        # Vector AB is point B - A

        # V1 = P2->P1 => V1 = P1 - P2
        # V2 = P2->P3 => V1 = P3 - P2
        V1 = P1 - P2
        V2 = P3 - P2

        # Magnitude of cross product is the area of the rhombus or rectangle between the two vectors
        # for a triangle we divide that by two
        return self.abs_cross_product(V1, V2) / 2
    
    # Get the angle in between two vectors counter clock wise counting
    def angle_between_two_vectors(self, V1, V2):
        # A·B = |A||B|cos(theta)
        # cos(theta) = (A·B)/|A||B|
        # theta = acos( (A·B) / (|A||B|) )
        V1, V2 = np.array(V1), np.array(V2)
        return np.arccos(
            np.dot(V1, V2) / (np.linalg.norm(V1) * np.linalg.norm(V2))
        )
    
    # P2 is the center point
    def angle_between_three_points(self, P1, P2, P3):
        P1, P2, P3 = np.array(P1), np.array(P2), np.array(P3)

        # P2 P1 = P1 - P2  /  P2 P3 = P3 - P2
        return self.angle_between_two_vectors(P1 - P2, P3 - P2)

    # A is proportional to B, C is what?
    def proportion(self, a, b, c):
        # a - b
        # c - x
        # x = b*c/a
        return (b*c)/a
    
    # https://stackoverflow.com/a/24468019/13477696
    def irregular_polygon_area(self, *points):
        n = len(points) # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        area = abs(area) / 2.0
        return area

    # Information of a point relative to a polygon
    # This function is overkill and 4x slower than checking against a rectangle for a rectangle
    def information_point_polygon(self, P, *polygon_points):
        """
        Given a point P and a polygon of N points, returns:
        {
            "is_inside": bool,
            "minimum_distance": float,
            "closest_point_index": see below
        }

        The minimum distance line is something like, you give this function
        (P=(x, y), (0, 0), (10, 5), (3, 5))  =>  (P, A, B, C)

        If point nearest line is AB, closest_point_index returns 0.

        AB - 0   CB - 1   CA - 2
        """

        # Get the area of the polygon
        polygon_area = self.irregular_polygon_area(*polygon_points)

        P = np.array(P)

        # Ordered points: (0, 0), (1, 0), (0, 1)  -->  [('A', (0, 0)), ('B', (1, 0)), ('C', (0, 1))]
        # We use list as those will be easier to manipulate
        op = [(self.num2col(i + 1), np.array(v)) for i, v in enumerate(polygon_points)]

        # [('A', (0, 0)), ('B', (1, 0)), ('C', (0, 1))] Becomes:
        # {'CAP': {'points': [array([0, 1]), array([0, 0]), array([1, 1])], 'area': 0.5}, 'ABP': {'points': ...
        triangles = {f"{op[i][0]}-{op[i+1][0]}-P": {"points": [op[i][1], op[i+1][1], P]} for i in range(-1, len(op) - 1)}
        
        # Now we convert to a dictionary for matching the points later on
        op = {point: coordinate for point, coordinate in op}

        # Calculate 
        for key in triangles.keys():
            triangles[key]["area"] = self.three_points_triangle_area(*triangles[key]["points"])

        # Sum the triangle areas
        triangles_areas = [triangles[key]["area"] for key in triangles.keys()]

        # The point is inside the polygon if the areas sum less than the original one
        is_inside = sum(triangles_areas) <= polygon_area

        # Get the triangle with the lowest area so we'll find the closest edge
        lowest_area = min(triangles_areas)
        for key in triangles.keys():
            if triangles[key]["area"] == lowest_area:
                smallest_triangle = key.split("-")
                break # This ignores equal area triangles posterior to this one, so the direction you send the coordinates matter

        # To get our closest_point_index
        # If the point is AB, we return 0
        # If the point is BC, we return 1
        # If the point is CA, we return 2
        # It is the lowest index of the two points
        point_indexes = [
            self.col2num(smallest_triangle[0]),
            self.col2num(smallest_triangle[1]),
        ]
        closest_point_index = min(point_indexes) - 1
        
        # # Find the minimum distance

        # Points A, B and point P
        smallest_triangle_points = [op[smallest_triangle[0]], op[smallest_triangle[1]], P]

        # In a special case where the max distance is a distance to a vertice (point is "outside" the line segment)
        # Triangle ABP, if either ABP or BAP is more than 90°
        # ABP are vectors BA and BP, BA = A - B and BP = P - B
        # BAP are vectors AB and AP, AB = B - A and AP = P - A
        A = smallest_triangle_points[0]
        B = smallest_triangle_points[1]
        BP = P - B
        AP = P - A
        ABP = abs(self.angle_between_two_vectors(A - B, P - B))
        BAP = abs(self.angle_between_two_vectors(B - A, P - A))

        if (ABP >= math.pi/2) or (BAP >= math.pi/2):
            if ABP > BAP:
                # The distance is between BP
                lowest_distance = np.linalg.norm(BP)
            else:
                # The distance is between AP
                lowest_distance = np.linalg.norm(AP)
        else:
            # Triangle in the form XX-YY-P, we'll find the height of the triangle, the minimum distance from P to 
            # the line of XX -- YY

            # The triangle base is the distance between the points (XX) and (YY) so..
            base = np.linalg.norm(
                [ smallest_triangle_points[0], smallest_triangle_points[1] ]
            )
            
            # We know its area, it's the lowest_area var!!
            # B*H = A,
            # H = A/B
            lowest_distance = lowest_area / base

        info = {
            "is_inside": is_inside,
            "distance": lowest_distance,
            "closest_point_index": closest_point_index,
        }

        return info

    # Is a point of coordinate P = (x, y) inside a rectangle R = (x, y, w, h)?
    # https://math.stackexchange.com/a/190117
    # This was a pretty fun insight :)
    def point_against_rectangle(self, P, rect):
        """
        R1 - - - - - - R2
         |     P       |
         |             |
        R3 - - - - - - R4

        Top left R1 is the center, w grows rightwards, h grows downwards
        """

        # Convert the point to a top left center Y grows downward
        # (negative all Y values so we flip the space on the X axis)
        P = [P[0], P[1]]

        # Rectangle

        x, y, w, h = [np.array(item) for item in rect]

        R1 = np.array([x, y])
        R2 = np.array([x + w, y])
        R3 = np.array([x, y + h])
        R4 = np.array([x + w, y + h])

        R1R2 = R2 - R1
        R1R3 = R3 - R1
        R1P  = P  - R1

        inside_height = (0 < np.dot(R1P, R1R3) < np.dot(R1R3, R1R3))
        inside_width  = (0 < np.dot(R1P, R1R2) < np.dot(R1R2, R1R2))

        is_inside = inside_height and inside_width

        # Get lowest distance to the rectangle
        dx = max(abs(P[0] - x) - w / 2, 0)
        dy = max(abs(P[1] - y) - h / 2, 0)
        lowest_distance = (dx * dx + dy * dy)**0.5

        info = {
            "is_inside": is_inside,
            "distance": lowest_distance,
            "closest_point_index": None,
        }

        return info

    # Skia uses raw X and Y for drawing --> (X1, Y1, X2, Y2)
    def rectangle_x_y_w_h_to_skia_rect(self, x, y, w, h):
        return [x, y, x + w, y + h]
    
    def rectangle_x_y_w_h_to_coordinates(self, x, y, w, h):
        return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]

if __name__ == "__main__":
    
    # Testing

    p = PysktProcessing({})


    for _ in range(1000):
        p.information_point_polygon((1, 0.1), (0, 0), (1, 0), (0, 1))

    # print( p.three_points_triangle_area([0, 0], [0, 3], [4, 0]) ) 

    # print(p.point_against_rectangle(
    #     [1, 0],
    #     [0, 0, 10, 10]
    # ))