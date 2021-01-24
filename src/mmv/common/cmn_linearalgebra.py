"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Set of 2D linear algebra, gotta put those LA engineering classes
and Gram Schmidt shenanigans into practice for once

Yes there is openblas, lapack and whatnot, I'm writing this myself
because it helps me to apply what I learned and think how to implement
stuff in Python in some other way I haven't tried yet :)

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

from mmv.common.cmn_utils import Utils
import mmv.common.cmn_any_logger
import math


# Define some basic N-dimentional linear algebra mechanisms
class LinearAlgebra:
    def __init__(self):
        self.utils = Utils()

    # Distance between two objects
    def distance(self, A, B):
        # Distance between two points
        if self.utils.is_matching_type([A, B], [LAPoint, LAPoint]):
            if len(A.coordinates) == len(B.coordinates):
                return ( sum([ (A.coordinates[i] - B.coordinates[i])**2 for i, _ in enumerate(A.coordinates) ]) )**0.5
            else:
                print("[LA ERROR] Dot product between vectors of different sizes: [%s] and [%s]" % A.coordinates, B.coordinates)
    
    # Dot product between two LAVectors
    def dot_product(self, A, B):
        if self.utils.is_matching_type([A, B], [LAVector, LAVector]):
            if len(A.coordinates) == len(B.coordinates):
                # Sum the multiplication of x1.x2.x3..xK + y1.y2.y3..yK + z1.z2.z3..zK +.. n1.n2.n3..nK
                return sum([A.coordinates[i] * B.coordinates[i] for i, _ in enumerate(A.coordinates)])
            else:
                print("[LA ERROR] Dot product between vectors of different sizes: [%s] and [%s]" % A.coordinates, B.coordinates)
        else:
            print("[LA ERROR] Can only calculate dot product between two vectors")

    # Get the angle between two vectors in radians
    def angle_between_two_vectors(self, A, B):
        if self.utils.is_matching_type([A, B], [LAVector, LAVector]):
            # The formula is ths one:
            # cos(angle) = a.b / |a||b|
            # We then just have to calculate angle = cos-1 ( a.b / |a||b| )
            # Where . is dot product and || the magnitude of a vector
            
            multiplied_magnitude = (A.magnitude() * B.magnitude())

            if not multiplied_magnitude == 0:

                # Get the cosine of the angle
                cos_angle = self.dot_product(A, B) / multiplied_magnitude
                
                # Rounding errors
                if cos_angle < -1:
                    cos_angle = -1
                elif cos_angle > 1:
                    cos_angle = 1

                # Return the angle itself got from cos-1
                return math.acos(cos_angle)
            else:
                return 0
        else:
            print("[LA ERROR] Can only calculate angle between two vectors in this function")

    # B is the mid point, so get the angle between the two vectors: BA and BC
    def angle_between_three_points(self, A, B, C):
        if self.utils.is_matching_type([A, B, C], [LAPoint, LAPoint, LAPoint]):

            # Create two vector objects
            va = LAVector()
            vb = LAVector()

            # Build them with the points
            va.from_two_points(B, A)
            vb.from_two_points(B, C)

            # Get the angle between two vectors
            angle = self.angle_between_two_vectors(va, vb)
            return angle
        else:
            print("[LA ERROR] Can only calculate angle between two vectors in this function")

# Define a LAPoint object with N dimentions
class LAPoint():
    def __init__(self, coordinates):
        self.coordinates = coordinates

# Define a LAVector object with N dimentions
class LAVector():
    def __init__(self):
        self.utils = Utils()

    # Build the coordinates from a given list of coordinates
    def from_coordinates(self, coordinates):
        self.coordinates = coordinates

    # Build the vector based on two points
    def from_two_points(self, A, B):
        # To get the direction and orientation of a vector based on two points, we have:
        # AB = B - A
        # So the result of B - A = (b1 - a1, b2 - a2, b3 - a3..., bn - an)
        if self.utils.is_matching_type([A, B], [LAPoint, LAPoint]):
            if len(A.coordinates) == len(B.coordinates):
                self.coordinates = [B.coordinates[i] - A.coordinates[i] for i, _ in enumerate(A.coordinates)]
            else:
                print("[LA POINT ERROR] Two points with different spaces")
        else:
            print("[LA VECTOR ERROR] Arguments aren't two LAPoint types")

    # Calculate the magnitude of a vector
    def magnitude(self):
        # Sum every square of the components and get the root of it
        return ( sum([x**2 for x in self.coordinates]) )**0.5


'''
# Here's some examples how this works

a = LAVector()
a.from_two_points(
    LAPoint([9, 10]),
    LAPoint([7, 6])
)

b = LAVector()
b.from_coordinates([3, 4])

c = LAPoint([1,2,3,4,5])
d = LAPoint([6,3,6,5,7])

l = LinearAlgebra()

print(l.angle_between_two_vectors(a, b))
print(a.magnitude())
print(l.distance(c, d))

print(l.angle_between_three_points(
    LAPoint([0, 5]),
    LAPoint([0, 0]),
    LAPoint([5, 0]),
))

'''