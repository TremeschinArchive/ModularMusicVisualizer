"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVSkiaImage object

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
from mmv.mmvskia.mmv_image_configure import MMVSkiaImageConfigure
from mmv.common.cmn_frame import Frame
from mmv.mmvskia.mmv_modifiers import *
import logging
import time
import skia
import uuid
import cv2


# Basically everything on MMV as we have to render images
class MMVSkiaImage:
    def __init__(self, mmvskia_main, depth = LOG_NO_DEPTH, from_generator = False) -> None:
        debug_prefix = "[MMVSkiaImage.__init__]"
        ndepth = depth + LOG_NEXT_DEPTH
        self.mmvskia_main = mmvskia_main
        self.preludec = self.mmvskia_main.prelude["mmvimage"]

        # Log the creation of this class
        if self.preludec["log_creation"] and not from_generator:
            logging.info(f"{depth}{debug_prefix} Created new MMVSkiaImage object, getting unique identifier for it")

        # Get an unique identifier for this MMVSkiaImage object
        self.identifier = self.mmvskia_main.utils.get_unique_id(
            purpose = "MMVSkiaImage object", depth = ndepth,
            silent = self.preludec["log_get_unique_id"] and from_generator
        )
        
        # The "animation" and path this object will follow
        self.animation = {}

        # Create classes
        self.configure = MMVSkiaImageConfigure(mmvskia_main = self.mmvskia_main, mmvimage_object = self)
        self.image = Frame()

        self.x = 0
        self.y = 0
        self.size = 1
        self.rotate_value = 0
        self.current_animation = 0
        self.current_step = -1
        self.is_deletable = False
        self.is_vectorial = False
        self.type = "mmvimage"

        # If we want to get the images from a video, be sure to match the fps!!
        self.video = None

        # Offset is the animations and motions this frame offset
        self.offset = [0, 0]

        self.ROUND = 3
        
        self._reset_effects_variables(depth = ndepth)

    # Clean this MMVSkiaImage's todo processing or applied
    def _reset_effects_variables(self, depth = LOG_NO_DEPTH):
        debug_prefix = "[MMVSkiaImage._reset_effects_variables]"
        ndepth = depth + LOG_NEXT_DEPTH
        
        # Log action
        if self.preludec["_reset_effects_variables"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Resetting effects variables (filters on image, mask, shaders, paint)")
        
        self.image_filters = []
        self.mask_filters = []
        # self.color_filters = []
        self.shaders = []
        self.paint_dict = {
            "AntiAlias": True
        }
    
    # Our Canvas is an MMVSkiaImage object so we reset it, initialize the animation layers automatically, bla bla
    # we don't need the actual configuration from the user apart from post processing accesses by this
    # MMVSkiaImage's MMVSkiaImageConfigure class
    def create_canvas(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImage.create_canvas]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Log action
        if self.preludec["create_canvas"]["log_action"]:
            logging.info(f"{depth}{debug_prefix} [{self.identifier}] Create empty canvas (this ought be the video canvas?)")

        # Will we be logging the steps?
        log_steps = self.preludec["create_canvas"]["log_steps"]

        # Initialize blank animation layer
        if log_steps:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Init animation layer")
        self.configure.init_animation_layer(depth = ndepth)
        
        # Reset the canvas, create new image of Contex's width and height
        if log_steps:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Reset canvas")
        self.reset_canvas(depth = ndepth)
        
        # Add Path Point at (0, 0)
        if log_steps:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Add required static path of type Point at (x, y) = (0, 0)")
        self.configure.add_path_point(x = 0, y = 0, depth = ndepth)
    
    # Create empty zeros canvas IMAGE, not CONTENTS.
    # If we ever wanna mirror the contents and apply post processing
    def reset_canvas(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImage.reset_canvas]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Hard debug, this should be executed a lot and we don't wanna clutter the log file or stdout
        if self.preludec["reset_canvas"]["log_action"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Reset canvas, create new image of Context's width and height in size")
            
        # Actually create the new canvas
        self.image.new(self.mmvskia_main.context.width, self.mmvskia_main.context.height)

    # Next step of animation
    def next(self, depth = LOG_NO_DEPTH) -> None:
        debug_prefix = "[MMVSkiaImage.next]"
        ndepth = depth + LOG_NEXT_DEPTH

        # Next step
        self.current_step += 1

        if self.preludec["next"]["log_current_step"]:
            logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Next step, current step = [{self.current_step}]")

        # Animation has ended, this current_animation isn't present on path.keys
        if self.current_animation not in list(self.animation.keys()):
            self.is_deletable = True
        
            # Log we are marked to be deleted
            if self.preludec["next"]["log_became_deletable"]:
                logging.debug(f"{ndepth}{debug_prefix} [{self.identifier}] Object is out of animation, marking to be deleted")

            return

        # The animation we're currently playing
        this_animation = self.animation[self.current_animation]

        animation = this_animation["animation"]
        steps = animation["steps"] * self.mmvskia_main.context.fps_ratio_multiplier  # Scale the interpolations

        # The current step is one above the steps we've been told, next animation
        if self.current_step >= steps + 1:
            self.current_animation += 1
            self.current_step = 0
            return
        
        # Reset offset, pending
        self.offset = [0, 0]
        self.image.pending = {}

        sg = time.time()

        self.image.reset_to_original_image()
        self._reset_effects_variables()

        position = this_animation["position"]
        path = position["path"]

        if "modules" in this_animation:
            
            
            modules = this_animation["modules"]

            self.is_vectorial = "vectorial" in modules

            # The video module must be before everything as it gets the new frame                
            if "video" in modules:
                s = time.time()

                this_module = modules["video"]

                # We haven't set a video capture or it has ended
                if self.video is None:
                    self.video = cv2.VideoCapture(this_module["path"])

                # Can we read next frame? if not, go back to frame 0 for a loop
                ok, frame = self.video.read()
                if not ok:  # cry
                    self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = self.video.read()
                
                # CV2 utilizes BGR matrix, but we need RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

                self.image.load_from_array(frame)
                self.image.resize_to_resolution(
                    width = this_module["width"],
                    height = this_module["height"],
                    override = True
                )

                if self.preludec["next"]["debug_timings"]:
                    logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Video module .next() took [{time.time() - s:.010f}]")

            if "rotate" in modules:
                s = time.time()
                
                this_module = modules["rotate"]
                rotate = this_module["object"]

                amount = rotate.next()
                amount = round(amount, self.ROUND)
                
                if not self.is_vectorial:
                    self.image.rotate(amount, from_current_frame=True)
                else:
                    self.rotate_value = amount

                if self.preludec["next"]["debug_timings"]:
                    logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Rotate module .next() took [{time.time() - s:.010f}]")

            if "resize" in modules:
                s = time.time()
                
                this_module = modules["resize"]
                resize = this_module["object"]

                # Where the vignetting intensity is pointing to according to our 
                resize.next()
                self.size = resize.get_value()

                if not self.is_vectorial:
                    
                    # If we're going to rotate, resize the rotated frame which is not the original image 
                    offset = self.image.resize_by_ratio( self.size, from_current_frame = True )

                    if this_module["keep_center"]:
                        self.offset[0] += offset[0]
                        self.offset[1] += offset[1]

                if self.preludec["next"]["debug_timings"]:
                    logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Resize module .next() took [{time.time() - s:.010f}]")

            # DONE
            if "blur" in modules:
                s = time.time()
                
                this_module = modules["blur"]
                blur = this_module["object"]

                blur.next()

                amount = blur.get_value()

                self.image_filters.append(
                    skia.ImageFilters.Blur(amount, amount)
                )

                if self.preludec["next"]["debug_timings"]:
                    logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Blur module .next() took [{time.time() - s:.010f}]")
            
            if "fade" in modules:
                s = time.time()
                
                this_module = modules["fade"]
                fade = this_module["object"]

                fade.next()
           
                self.image.transparency( fade.get_value() )

                if self.preludec["next"]["debug_timings"]:
                    logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Fade module .next() took [{time.time() - s:.010f}]")
                    
            # Apply vignetting
            if "vignetting" in modules:
                s = time.time()
                
                this_module = modules["vignetting"]
                vignetting = this_module["object"]

                # Where the vignetting intensity is pointing to according to our 
                vignetting.next()
                vignetting.get_center()
                next_vignetting = vignetting.get_value()

                # This is a somewhat fake vignetting, we just start a black point with full transparency
                # at the center and make a radial gradient that is black with no transparency at the radius
                self.mmvskia_main.skia.canvas.drawPaint({
                    'Shader': skia.GradientShader.MakeRadial(
                        center=(vignetting.center_x, vignetting.center_y),
                        radius=next_vignetting,
                        colors=[skia.Color4f(0, 0, 0, 0), skia.Color4f(0, 0, 0, 1)]
                    )
                })

                if self.preludec["next"]["debug_timings"]:
                    logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Vignetting module .next() took [{time.time() - s:.010f}]")

            
            if "vectorial" in modules:
                s = time.time()
                
                this_module = modules["vectorial"]
                vectorial = this_module["object"]

                effects = {
                    "size": self.size,
                    "rotate": self.rotate_value,
                    "image_filters": self.image_filters,
                }

                # Visualizer blit itself into the canvas automatically
                vectorial.next(effects)

                if self.preludec["next"]["debug_timings"]:
                    logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Vectorial module .next() took [{time.time() - s:.010f}]")

            if self.preludec["next"]["debug_timings"]:
                logging.debug(f"{depth}{debug_prefix} [{self.identifier}] Global .next() took [{time.time() - sg:.010f}]")

        # Iterate through every position module
        for modifier in path:
            
            # # Override modules

            argument = [self.x, self.y] + self.offset

            # Move according to a Point (be stationary)
            if self.mmvskia_main.utils.is_matching_type([modifier], [MMVSkiaModifierPoint]):
                # Attribute (x, y) to Point's x and y
                [self.x, self.y], self.offset = modifier.next(*argument)

            # Move according to a Line (interpolate current steps)
            if self.mmvskia_main.utils.is_matching_type([modifier], [MMVSkiaModifierLine]):
                # Interpolate and unpack next coordinate
                [self.x, self.y], self.offset = modifier.next(*argument)

            # # Offset modules

            # Get next shake offset value
            if self.mmvskia_main.utils.is_matching_type([modifier], [MMVSkiaModifierShake]):
                [self.x, self.y], self.offset = modifier.next(*argument)

    # Blit this item on the canvas
    def blit(self) -> None:

        # Vectorial objects blit themselves on a .next() function
        if self.is_vectorial:
            return

        # Invert x and y because top left is (0, 0), y first
        y = int(self.x + self.offset[1])
        x = int(self.y + self.offset[0])

        if self.mask_filters:
            self.paint_dict["MaskFilter"] = self.mask_filters
    
        if self.image_filters:
            self.paint_dict["ImageFilter"] = skia.ImageFilters.Merge(self.image_filters)

        # Get a paint with the options, image filters (if any) for skia to draw
        paint = skia.Paint(self.paint_dict)

        # Blit this image
        self.mmvskia_main.skia.canvas.drawImage(
            self.image.image, x, y,
            paint = paint,
        )
