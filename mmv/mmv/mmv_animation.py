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

from mmv.mmv_classes import *
from mmv.mmv_visualizer import MMVVisualizer
from mmv.mmv_image import MMVImage
from mmv.mmv_generator import *
from mmv.mmv_modifiers import *
import random
import copy
import math
import os


# Store and sorta "organize" the many MMV objects we can have on a given scene
class MMVAnimation:
    
    # Initialize a MMVAnimation class with required arguments
    def __init__(self, context: Context, controller: Controller, audio: Audio, canvas: Canvas) -> None:
        
        # Get the classes
        self.context = context
        self.controller = controller
        self.audio = audio
        self.canvas = canvas

        # Content are the MMV objects stored that gets rendered on the screen
        # generators are MMVGenerators that we get new objects from
        self.content = {}
        self.generators = []

    # Make layers until a given N value
    def mklayers_until(self, n: int) -> None:
        for layer_index in range(n + 1):  # n + 1 because range() is exclusive at the end ( range(2) = [0, 1] )
            if not layer_index in self.content.keys():
                self.content[n] = []
    
    # Call every next step of the content animations
    def next(self, fftinfo: dict, this_step: int) -> None:

        # Iterate through the generators
        for item in self.generators:

            # Get what the generator has to offer
            new = item.next(fftinfo, this_step)

            # The response object (if any [None]) and layer to instert on this self.content
            new_object = new["object"]

            # Object is not null, add it to the said layer
            if not new_object == None:
                self.content[new["layer"]].append(new_object)

        # Dictionary of layers and item indexes on that layer to delete
        items_to_delete = {}

        for layer_index in sorted(list(self.content.keys())):
            for position, item in enumerate(self.content[layer_index]):

                # We can delete the item as it has decided life wasn't worth anymore
                if item.is_deletable:
                    
                    # Create empty list if key doesn't exist
                    if layer_index not in items_to_delete:
                        items_to_delete[layer_index] = []

                    # Append item position on layer index
                    items_to_delete[layer_index].append(position)
                    continue

                # Generate next step of animation
                item.next(fftinfo, this_step)

                # Blit itself on the canvas
                if not self.context.multiprocessed:
                    item.blit(self.canvas)

        # For each layer index we have items to delete
        for layer_index in items_to_delete.keys():
            # For each item in the REVERSED list of items indexes to delete,
            # otherwise we break out iteration and index linking
            for items in sorted(items_to_delete[layer_index], reverse=True):
                del self.content[ layer_index ][ items ]

        # Post process this final frame as we added all the items
        self.canvas.next(fftinfo, this_step)
