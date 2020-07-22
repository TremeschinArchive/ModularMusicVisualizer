"""
===============================================================================

Purpose: Canvas to draw on

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

from mmv.common.utils import Utils
from mmv.common.frame import Frame
import os


class Canvas():
    def __init__(self, context):

        debug_prefix = "[Canvas.__init__]"

        self.context = context
        self.utils = Utils()

        # Create new canvas
        self.canvas = Frame()
        self.reset_canvas()

        # Processing variables
        self.post_processing = {}
        self.vignetting = 0
        self.current_step = 0

    def reset_canvas(self):

        debug_prefix = "[Canvas.reset_canvas]"

        # Our Canvas is a blank Frame class
        # self.canvas = Frame()
        self.canvas.new(self.context.width, self.context.height, transparent=True)

    # Next step of animation
    def next(self, fftinfo):

        debug_prefix = "[Canvas.next]"

        # No post processing
        if len(list(self.post_processing.keys())) == 0:
            return
        
        self.canvas.pending = {}

        # There is some post processing
        for key in sorted(list(self.post_processing.keys())):

            # The animation we're currently processing
            this_post_processing = self.post_processing[key]
            
            # Is there any modules in this animation?
            if "modules" in this_post_processing:

                module = this_post_processing["modules"]

                # Apply vignetting
                if "vignetting" in module:
                    
                    # The module we're working with
                    this_module = module["vignetting"]

                    # TODO: needed?
                    # Limit the average
                    average = fftinfo["average_value"]

                    if average > 1:
                        average = 1
                    if average < -0.9:
                        average = -0.9

                    # Where the vignetting intensity is pointing to according to our 
                    towards = eval(
                        this_module["activation"].replace("X", str(average))
                    )

                    # Minimum vignetting
                    minimum = this_module["minimum"] 
                    if towards < minimum:
                        towards = minimum

                    # Interpolate to a new vignetting value
                    new_vignetting = this_module["interpolation"](
                        self.vignetting,
                        towards,
                        self.current_step,
                        this_post_processing["steps"],
                        self.vignetting,
                        this_module["arg_a"]
                    )

                    # Apply the new vignetting effect on the center of the screen

                    if self.context.multiprocessed:
                        self.canvas.pending["vignetting"] = [
                            self.context.width//2,
                            self.context.height//2,
                            new_vignetting,
                            new_vignetting,
                        ]
                    else:
                        self.canvas.vignetting(
                            self.context.width//2,
                            self.context.height//2,
                            new_vignetting,
                            new_vignetting
                        )

                    # Update vignetting value
                    self.vignetting = new_vignetting

                    # print(debug_prefix, "vignetting", new_vignetting, "to", towards)

                if "glitch" in module:

                    this_module = module["glitch"]

                    ammount = eval(this_module["activation"].replace("X", str(fftinfo["average_value"])))

                    color_offset = this_module["color_offset"]
                    scan_lines = this_module["scan_lines"]

                    if self.context.multiprocessed:
                        self.canvas.pending["glitch"] = [ammount, color_offset, scan_lines]
                    else:
                        self.canvas.glitch(ammount, color_offset, scan_lines)
                        
        # Next step of animation
        self.current_step += 1
    
    def resolve_pending(self):
        self.canvas.resolve_pending()
