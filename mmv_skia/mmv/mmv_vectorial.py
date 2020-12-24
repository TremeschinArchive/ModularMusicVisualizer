"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Wrapper for MMV modules that write directly to the canvas like
the visualizer bars, progression bar

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

from mmv.mmv_progression_bar import MMVProgressionBarVectorial
from mmv.mmv_piano_roll import MMVPianoRollVectorial
from mmv.mmv_music_bar import MMVMusicBarsVectorial


class MMVVectorial:
    def __init__(self, mmv, **kwargs) -> None:
        self.mmv = mmv

        debug_prefix = "[MMVVectorial.__init__]"

        # For the kwargs see each class

        # Visualizer bars
        if kwargs["vectorial_type_class"] == "visualizer":
            print(debug_prefix, "Add MMVMusicBars, kwargs:", kwargs)
            self.next_object = MMVMusicBarsVectorial(
                mmv = self.mmv,
                **kwargs,
            )
        
        # Progression bar object
        elif kwargs["vectorial_type_class"] == "progression-bar":
            print(debug_prefix, "Add MMVProgressionBar, kwargs:", kwargs)
            self.next_object = MMVProgressionBarVectorial(
                mmv = self.mmv,
                **kwargs,
            )
        
        # Progression bar object
        elif kwargs["vectorial_type_class"] == "piano-roll":
            print(debug_prefix, "Add MMVPianoRollVectorial, kwargs:", kwargs)
            self.next_object = MMVPianoRollVectorial(
                mmv = self.mmv,
                **kwargs,
            )
        
        else:
            raise RuntimeError(debug_prefix, "No valid vectorial_type_class set, kwargs:", kwargs)

    # Next function
    def next(self, effects):
        self.next_object.next(
            effects = effects
        )