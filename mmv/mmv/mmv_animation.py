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

from mmv.common.interpolation import Interpolation
from mmv.mmv_visualizer import MMVVisualizer
from mmv.common.functions import Functions
from mmv.mmv_image import MMVImage
from mmv.common.utils import Utils
from mmv.mmv_generator import *
from mmv.mmv_modifiers import *
import random
import copy
import math
import os


class MMVAnimation():
    def __init__(self, context, controller, audio, canvas):
        self.context = context
        self.controller = controller
        self.audio = audio
        self.canvas = canvas

        self.interpolation = Interpolation()
        self.functions = Functions()
        self.utils = Utils()

        self.content = {}
        self.generators = []

        n_layers = 10
        for n in range(n_layers):
            self.content[n] = []
    
    # Call every next step of the content animations
    def next(self, fftinfo, this_step):

        for item in self.generators:

            # Get what the generator has to offer
            new = item.next(fftinfo, this_step)

            # The response object (if any [None]) and layer to instert on this self.content
            new_object = new["object"]

            # Object is not null, add it to the said layer
            if not new_object == None:
                self.content[new["layer"]].append(new_object)

        items_to_delete = []

        for layer in sorted(list(self.content.keys())):
            for position, item in enumerate(self.content[layer]):

                # We can delete the item as it has decided life wasn't worth anymore
                if item.is_deletable:
                    items_to_delete.append([layer, position])
                    continue

                # Generate next step of animation
                item.next(fftinfo, this_step)

                # Blit itself on the canvas
                if not self.context.multiprocessed:
                    item.blit(self.canvas)

        for items in sorted(items_to_delete, reverse=True):
            del self.content[ items[0] ][ items[1] ]

        # Post process this final frame as we added all the items
        self.canvas.next(fftinfo, this_step)
