"""
===============================================================================

Purpose: MMVAnimation object

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

from mmvparticle import MMVParticle
from modifiers import Point
from modifiers import Line
import random


class MMVAnimation():
    def __init__(self, context, controller, canvas):
        self.context = context
        self.controller = controller
        self.canvas = canvas

        self.content = {}

    # Call every next step of the content animations
    def next(self):
        for zindex in sorted(list(self.content.keys())):
            for item in self.content[zindex]:
                # Generate next step of animation
                item.next()

                # Blit itself on the canvas
                item.blit(self.canvas)

    # Generate the objects on the animation
    # TODO: PROFILES, CURRENTLY MANUALLY SET HERE
    def generate(self):
        
        particles = []

        for _ in range(100):
            temp = MMVParticle(self.context)

            x1 = random.randint(100, 1000)
            y1 = random.randint(100, 500)
            x2 = random.randint(100, 1000)
            y2 = random.randint(100, 500)
            x3 = random.randint(100, 1000)
            y3 = random.randint(100, 500)

            temp.path[0] = {
                "position": Line(
                    (x1, y1),
                    (x2, y2),
                ),
                "steps": 100
            }
            temp.path[1] = {
                "position": Line(
                    (x2, y2),
                    (x3, y3),
                ),
                "steps": 200
            }


            particles.append(temp)

        print("Generating, adding mmvparticle")
        self.content[0] = particles
