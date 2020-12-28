"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVSkiaAnimation object

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

from mmv.common.cmn_constants import LOG_NEXT_DEPTH, LOG_NO_DEPTH
from mmv.mmvskia.mmv_generator import *
from mmv.mmvskia.mmv_modifiers import *
import logging
import random
import copy
import math
import os


# Store and sorta "organize" the many MMV objects we can have on a given scene
class MMVSkiaAnimation:

    # Initialize a MMVSkiaAnimation class with required arguments
    def __init__(self, mmv_main, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaAnimation.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmv_main = mmv_main
        self.preludec = self.mmv_main.prelude["mmvanimation"]

        # Log we started
        if self.preludec["log_creation"]:
            logging.info(f"{depth}{debug_prefix} Creating empty content and generators dictionary and list respectively")

        # Content are the MMV objects stored that gets rendered on the screen
        # generators are MMVSkiaGenerators that we get new objects from
        self.content = {}
        self.generators = []

    # Make layers until a given N value
    def mklayers_until(self, n: int, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaAnimation.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Hard debug this action
        if self.preludec["mklayers_until"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} Making animation layers until N = [{n}]")

        # n + 1 because range() is exclusive at the end ( range(2) = [0, 1] )
        # and we use "human numbers" starting at 1
        for layer_index in range(n + 1):  

            # If we need to create this empty animation layer (list)
            if layer_index not in list(self.content.keys()):

                # Log that we'll be doing so
                if self.preludec["mklayers_until"]["log_new_layers"]:
                    logging.info(f"{depth}{debug_prefix} Animation layer index N = [{layer_index}] didn't existed, creating empty list")

                # Create empty list at
                self.content[layer_index] = []

    # Call every next step of the content animations
    def next(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaAnimation.next]"
        ndepth = depth + LOG_NEXT_DEPTH
        
        # Iterate through the generators
        for item in self.generators:

            # Get what the generator has to offer, a list
            new = item.next()

            # For each returned new stuff from generator
            for new_object in new:

                # The response object (if any [None]) and layer to insert on this self.content
                object_to_add = new_object["object"]

                # Object is not null, add it to the said layer
                if object_to_add is not None:
                    layer = new_object["layer"]
                    self.mklayers_until(layer)
                    self.content[layer].append(object_to_add)

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

                # Generate and draw next step of animation
                item.next()
                item.blit()

        # For each layer index we have items to delete
        for layer_index in items_to_delete.keys():
            # For each item in the REVERSED list of items indexes to delete,
            # otherwise we break out iteration and index linking
            for items in sorted(items_to_delete[layer_index], reverse = True):
                del self.content[ layer_index ][ items ]

        # Post process this final frame as we added all the items
        self.mmv_main.canvas.next()
