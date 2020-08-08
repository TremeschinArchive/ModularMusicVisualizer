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
import math
import copy
import skia
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
        self.overlay_mode = "composite"  # composite and copy

        # If we want to get the images from a video, be sure to match the fps!!
        self.video = None

        # Offset is the animations and motions this frame offset
        self.offset = [0, 0]

        self.ROUND = 3
        
        self._reset_effects_variables()

    def _reset_effects_variables(self):
        self.image_filters = []
        self.mask_filters = []
        # self.color_filters = []
        self.shaders = []
        self.paint_dict = {
            "AntiAlias": True
        }
    
    # Our Canvas is an MMVImage object
    def create_canvas(self) -> None:
        self.configure.init_animation_layer()
        self.reset_canvas()
        self.configure.add_path_point(0, 0)
    
    def reset_canvas(self) -> None:
        self.image.new(self.context.width, self.context.height)

    # Don't pickle cv2 video  
    def __getstate__(self):
        state = self.__dict__.copy()
        if "video" in state:
            del state["video"]
        return state
    
    # Next step of animation
    def next(self, fftinfo: dict, this_step: int, skia_canvas=None) -> None:

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
        self._reset_effects_variables()

        position = this_animation["position"]
        path = position["path"]

        if "modules" in this_animation:
            
            modules = this_animation["modules"]

            if "visualizer" in modules:

                this_module = modules["visualizer"]

                visualizer = this_module["object"]

                self.image.load_from_array(visualizer.next(fftinfo))

            # The video module must be before everything as it gets the new frame                
            if "video" in modules:

                this_module = modules["video"]

                # We haven't set a video capture or it has ended
                if self.video == None:
                    self.video = cv2.VideoCapture(this_module["path"])

                # Can we read next frame? if not, go back to frame 0 for a loop
                ok, frame = self.video.read()
                if not ok:  # cry
                    self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = self.video.read()
                
                # CV2 utilizes BGR matrix, but we need RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                shake = 0

                for modifier in position:
                    if self.utils.is_matching_type([modifier], [MMVModifierShake]):
                        shake = modifier.distance

                width = self.context.width + (2*shake)
                height = self.context.height + (2*shake)
            
                self.image.load_from_array(frame)
                self.image.resize_to_resolution(
                    width, height,
                    override=True
                )

            if "rotate" in modules:
                this_module = modules["rotate"]
                rotate = this_module["object"]

                amount = rotate.next()
                amount = round(amount, self.ROUND)
                
                self.image.rotate(amount, from_current_frame=True)

            if "resize" in modules:

                this_module = modules["resize"]
                resize = this_module["object"]

                # Where the vignetting intensity is pointing to according to our 
                resize.next(fftinfo["average_value"])
                self.size = resize.get_value()

                # If we're going to rotate, resize the rotated frame which is not the original image 
                offset = self.image.resize_by_ratio( self.size, from_current_frame = True )

                if this_module["keep_center"]:
                    self.offset[0] += offset[0]
                    self.offset[1] += offset[1]

            # DONE
            if "blur" in modules:

                this_module = modules["blur"]
                blur = this_module["object"]

                blur.next(fftinfo["average_value"])

                amount = blur.get_value()

                self.image_filters.append(
                    skia.ImageFilters.Blur(amount, amount)
                )
            
            if "fade" in modules:

                this_module = modules["fade"]
                fade = this_module["object"]

                fade.next(fftinfo["average_value"])
           
                self.image.transparency( fade.get_value() )
                    
            # Apply vignetting
            if "vignetting" in modules:

                this_module = modules["vignetting"]
                vignetting = this_module["object"]

                # Where the vignetting intensity is pointing to according to our 
                vignetting.next(fftinfo["average_value"])
                vignetting.get_center()
                next_vignetting = vignetting.get_value()

                
                skia_canvas.canvas.drawPaint({
                    'Shader': skia.GradientShader.MakeRadial(
                        center=(vignetting.center_x, vignetting.center_y),
                        radius=next_vignetting,
                        colors=[skia.Color4f(0, 0, 0, 0), skia.Color4f(0, 0, 0, 1)]
                    )
                })


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
    def blit(self, blit_to_skia) -> None:

        y = int(self.x + self.offset[1])
        x = int(self.y + self.offset[0])

        if self.mask_filters:
            self.paint_dict["MaskFilter"] =  self.mask_filters
    
        if self.image_filters:
            self.paint_dict["ImageFilter"] = skia.ImageFilters.Merge(self.image_filters)

        image = self.image.image
        
        paint = skia.Paint(self.paint_dict)

        blit_to_skia.canvas.drawImage(
            image, x, y,
            paint = paint,
        )

        return

        """  
        if angle == 0:

            paint = skia.Paint(self.paint_dict)

            blit_to_skia.canvas.drawImage(
                image, x, y,
                paint = paint,
            )
        else:
            paint = skia.Paint(self.paint_dict)

            blit_to_skia.canvas.translate(x/2, y/2)
            blit_to_skia.canvas.rotate(angle)

            blit_to_skia.canvas.drawImage(
                image, x, y,
                paint = paint,
            )

            blit_to_skia.canvas.rotate(-angle)
            blit_to_skia.canvas.translate(- x/2, - y /2)
        
        """

    def resolve_pending(self) -> None:
        self.image.resolve_pending()

