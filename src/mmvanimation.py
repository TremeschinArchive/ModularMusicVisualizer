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

class MMVAnimation():
    def __init__(self, context):
        self.context = context
        self.content = {
            
        }

    def next(self):
        for zindex in sorted(self.content.keys()):
            for item in self.content[zindex].keys():
                item.next()

    def generate(self):
        self.content[0] = [MMVParticle() for _ in range(1)]