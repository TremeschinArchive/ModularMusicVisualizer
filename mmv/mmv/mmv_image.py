"""
===============================================================================

Purpose: MMVImage object

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

from mmv.mmv_image_configure import MMVImageConfigure
from mmv.mmv_interpolation import MMVInterpolation
from mmv.common.cmn_functions import Functions
from mmv.mmv_visualizer import MMVVisualizer
from mmv.common.cmn_frame import Frame
from mmv.common.cmn_utils import Utils
from mmv.mmv_context import Context
from mmv.common.cmn_types import *
from mmv.mmv_modifiers import *
import copy
import cv2
import os


# Basically everything on MMV as we have to render images
class MMVImage:

    def __init__(self, context: Context) -> None:
        
        debug_prefix = "[MMVImage.__init__]"
        
        self.context = context

        # The "animation" and path this object will follow
        self.animation = {}

        # Create classes
        self.configure = MMVImageConfigure(self)
        self.functions = Functions()
        self.utils = Utils()
        self.image = Frame()

        self.x = 0
        self.y = 0
        self.size = 1
        self.current_animation = 0
        self.current_step = -1
        self.is_deletable = False
        self.type = "mmvimage"

        # If we want to get the images from a video, be sure to match the fps!!
        self.video = None

        # Offset is the animations and motions this frame offset
        self.offset = [0, 0]

        self.ROUND = 3
    
    # Our Canvas is an MMVImage object
    def create_canvas(self) -> None:
        self.configure.init_animation_layer()
        self.reset_canvas()
        self.configure.add_path_point(0, 0)
    
    def reset_canvas(self) -> None:
        self.image.new(self.context.width, self.context.height, transparent=True)

    # Don't pickle cv2 video  
    def __getstate__(self):
        state = self.__dict__.copy()
        if "video" in state:
            del state["video"]
        return state
    
    # Next step of animation
    def next(self, fftinfo: dict, this_step: int) -> None:

        self.current_step += 1

        # Animation has ended, this current_animation isn't present on path.keys
        if not self.current_animation in list(self.animation.keys()):
            self.is_deletable = True
            return

        # The animation we're currently playing
        this_animation = self.animation[self.current_animation]

        animation = this_animation["animation"]
        steps = animation["steps"]

        # The current step is one above the steps we've been told, next animation
        if self.current_step == steps + 1:
            self.current_animation += 1
            self.current_step = 0
            return
        
        # Reset offset, pending
        self.offset = [0, 0]
        self.image.pending = {}

        self.image._reset_to_original_image()

        position = this_animation["position"]
        path = position["path"]

        if "modules" in this_animation:
            
            modules = this_animation["modules"]

            if "visualizer" in modules:

                this_module = modules["visualizer"]

                visualizer = this_module["object"]

                if self.context.multiprocessed:
                    visualizer.next(fftinfo, is_multiprocessing=True)
                    self.image.pending["visualizer"] = [
                        copy.deepcopy(visualizer), fftinfo
                    ]
                    self.image.width = visualizer.config["width"]
                    self.image.height = visualizer.config["height"]

                else:
                    self.image.load_from_array(
                        visualizer.next(fftinfo),
                        convert_to_png=True
                    )

            # The video module must be before everything as it gets the new frame                
            if "video" in modules:

                this_module = modules["video"]

                # We haven't set a video capture or it has ended
                if self.video == None:
                    self.video = cv2.VideoCapture(path)

                # Can we read next frame? if not, go back to frame 0 for a loop
                ok, frame = self.video.read()
                if not ok:  # cry
                    self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = self.video.read()
                
                # CV2 utilizes BGR matrix, but we need RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                shake = 0

                for position in positions:
                    if self.utils.is_matching_type([position], [MMVModifierShake]):
                        shake = position.distance

                width = self.context.width + (2*shake)
                height = self.context.height + (2*shake)
                
                if self.context.multiprocessed:
                    self.image.pending["video"] = [
                        copy.deepcopy(frame),
                        width, height
                    ]
                    self.image.width = width
                    self.image.height = height
                else:
                    self.image.load_from_array(frame, convert_to_png=True)
                    self.image.resize_to_resolution(
                        width, height,
                        override=True
                    )

            if "rotate" in modules:
                this_module = modules["rotate"]
                rotate = this_module["object"]

                amount = rotate.next()
                amount = round(amount, self.ROUND)
                
                if self.context.multiprocessed:
                    self.image.pending["rotate"] = [amount]
                else:
                    self.image.rotate(amount)

            if "resize" in modules:
                this_module = modules["resize"]
                resize = this_module["object"]

                # Where the vignetting intensity is pointing to according to our 
                resize.next(fftinfo["average_value"])
                self.size = resize.get_value()

                if self.context.multiprocessed:
                    self.image.pending["resize"] = [self.size]
                    offset = self.image.resize_by_ratio(
                        self.size, get_only_offset=True
                    )
                else:
                    offset = self.image.resize_by_ratio(
                        # If we're going to rotate, resize the rotated frame which is not the original image
                        self.size, from_current_frame="rotate" in modules
                    )

                if this_module["keep_center"]:
                    self.offset[0] += offset[0]
                    self.offset[1] += offset[1]

            if "blur" in modules:

                this_module = modules["blur"]

                amount = eval(this_module["activation"].replace("X", str(fftinfo["average_value"])))
                amount = round(amount, self.ROUND)

                if self.context.multiprocessed:
                    self.image.pending["blur"] = [amount]
                else:
                    self.image.gaussian_blur(amount)
            
            if "glitch" in modules:

                this_module = modules["glitch"]

                amount = eval(this_module["activation"].replace("X", str(fftinfo["average_value"])))
                amount = round(amount, self.ROUND)

                color_offset = this_module["color_offset"]
                scan_lines = this_module["scan_lines"]

                if self.context.multiprocessed:
                    self.image.pending["glitch"] = [amount, color_offset, scan_lines]
                else:
                    self.image.glitch(amount, color_offset, scan_lines)

            if "fade" in modules:

                this_module = modules["fade"]
                fade = this_module["object"]

                fade.next(fftinfo["average_value"])
           
                if self.context.multiprocessed:
                    self.image.pending["transparency"] = [ fade.get_value() ]
                else:
                    self.image.transparency( fade.get_value() )
                    
            # Apply vignetting
            if "vignetting" in modules:

                this_module = modules["vignetting"]
                vignetting = this_module["object"]

                # Where the vignetting intensity is pointing to according to our 
                vignetting.next(fftinfo["average_value"])
                vignetting.get_center()
                next_vignetting = vignetting.get_value()

                # Apply the new vignetting effect on the center of the image
                if self.context.multiprocessed:
                    self.image.pending["vignetting"] = [
                        vignetting.center_x,
                        vignetting.center_y,
                        next_vignetting,
                        next_vignetting,
                    ]
                else:
                    self.image.vignetting(
                        vignetting.center_x,
                        vignetting.center_y,
                        next_vignetting,
                        next_vignetting
                    )


        # Iterate through every position module
        for modifier in path:
            
            # # Override modules

            argument = [self.x, self.y] + self.offset

            # Move according to a Point (be stationary)
            if self.utils.is_matching_type([modifier], [MMVModifierPoint]):
                # Atribute (x, y) to Point's x and y
                [self.x, self.y], self.offset = modifier.next(*argument)

            # Move according to a Line (interpolate current steps)
            if self.utils.is_matching_type([modifier], [MMVModifierLine]):
                # Interpolate and unpack next coordinate
                [self.x, self.y], self.offset = modifier.next(*argument)

            # # Offset modules

            # Get next shake offset value
            if self.utils.is_matching_type([modifier], [MMVModifierShake]):
                [self.x, self.y], self.offset = modifier.next(*argument)

    # Blit this item on the canvas
    def blit(self, canvas: Frame) -> None:

        x = int(self.x + self.offset[1])
        y = int(self.y + self.offset[0])

        canvas.overlay_transparent(
            self.image.array,
            y, x
        )

        # This is for trivia / future, how it used to work until overlay_transparent wasn't slow anymore
        # img = self.image
        # width, height, _ = img.frame.shape
        # canvas.canvas.copy_from(
        #     self.image.array,
        #     canvas.canvas.frame,
        #     [0, 0],
        #     [x, y],
        #     [x + width - 1, y + height - 1]
        # )

    def resolve_pending(self) -> None:
        self.image.resolve_pending()

