"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVProgressionBar object

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

from mmv.mmvskia.progression_bars.mmv_progression_bar_rectangle import MMVSkiaProgressionBarRectangle
from mmv.mmvskia.mmv_modifiers import *
from mmv.common.cmn_frame import Frame
from mmv.common.cmn_utils import Utils
import random
import math
import os


class MMVSkiaProgressionBarVectorial:
    """
    kwargs:
    {
        "type": Determines what class of Progression Bar we'll use
            "rectangle": MMVSkiaProgressionBarRectangle

        "rectangle": MMVSkiaProgressionBarRectangle
            {
                "position": str, "bottom"
                    ["bottom", "top"]
            }
        
        "shake_scalar": float, 14
    
    }
    """
    def __init__(self, mmv, **kwargs) -> None:
        
        debug_prefix = "[MMVSkiaProgressionBarVectorial.__init__]"
        
        self.mmv = mmv
        self.config = {}

        self.utils = Utils()

        self.path = {}

        self.x = 0
        self.y = 0
        self.size = 1
        self.is_deletable = False
        self.offset = [0, 0]

        self.image = Frame()

        # General Configuration

        self.config["type"] = kwargs.get("bar_type", "rectangle")
        self.config["position"] = kwargs.get("position", "bottom")
        self.config["shake_scalar"] = kwargs.get("shake_scalar", 14)

        # We have different files with different classes of ProgressionBars

        # Simple, rectangle bar
        if self.config["type"] == "rectangle":
            print(debug_prefix, "Builder is MMVSkiaProgressionBarRectangle")
            self.builder = MMVSkiaProgressionBarRectangle(self, self.mmv)
        
        else:
            raise RuntimeError(debug_prefix, "No valid builder set, kwargs:", kwargs, "config:", self.config)

    # Call builder for drawing directly on the canvas
    def next(self, effects):
        self.builder.build(self.config, effects)

  