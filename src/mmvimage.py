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

from interpolation import Interpolation
from modifiers import *
from frame import Frame
from utils import Utils
import copy
import cv2
import os


class MMVImage():
    def __init__(self, context):
        
        debug_prefix = "[MMVImage.__init__]"
        
        self.context = context

        self.interpolation = Interpolation()
        self.utils = Utils()

        self.path = {}

        self.x = 0
        self.y = 0
        self.size = 1
        self.current_animation = 0
        self.current_step = 0
        self.is_deletable = False
        self.type = "mmvimage"

        # If we want to get the images from a video, be sure to match the fps!!
        self.video = None

        # Base offset is the default offset when calling .next at the end
        # Offset is the animations and motions this frame offset
        self.base_offset = [0, 0]
        self.offset = [0, 0]

        # Create Frame and load random particle
        self.image = Frame()
        
    # Next step of animation
    def next(self, fftinfo, this_step):

        # Animation has ended, this current_animation isn't present on path.keys
        if not self.current_animation in list(self.path.keys()):
            # print("No more animations, quitting")
            self.is_deletable = True
            return

        # The animation we're currently playing
        this_animation = self.path[self.current_animation]
        
        # The current step is one above the steps we've been told, next animation
        if self.current_step == this_animation["steps"] + 1:
            # print("Out of steps, next animation")
            self.current_animation += 1
            self.current_step = 0
            return
        
        # Reset offset, pending
        self.offset = [0, 0]
        self.image.pending = {}

        positions = this_animation["position"]
        steps = this_animation["steps"]

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
                    self.video = cv2.VideoCapture(this_module["path"])

                # Can we read next frame? if not, go back to frame 0 for a loop
                ok, frame = self.video.read()
                if not ok:  # cry
                    self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ok, frame = self.video.read()
                
                # CV2 utilizes BGR matrix, but we need RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                if self.context.multiprocessed:
                    self.image.pending["video"] = [
                        copy.deepcopy(frame),
                        self.context.width + (2*this_module["shake"]),
                        self.context.height + (2*this_module["shake"])
                    ]
                else:
                    self.image.load_from_array(frame, convert_to_png=True)
                    self.image.resize_to_resolution(
                        self.context.width + (2*this_module["shake"]),
                        self.context.height + (2*this_module["shake"]),
                        override=True
                    )

            if "rotate" in modules:

                this_module = modules["rotate"]
                rotate = this_module["object"]
                
                if self.context.multiprocessed:
                    self.image.pending["rotate"] = [
                        rotate.next()
                    ]
                else:
                    self.image.rotate(rotate.next())

            if "resize" in modules:

                this_module = modules["resize"]
        
                a = fftinfo["average_value"]

                if a > 1:
                    a = 1
                if a < -0.9:
                    a = -0.9

                a = this_module["interpolation"](
                    self.size,
                    eval(this_module["activation"].replace("X", str(a))),
                    self.current_step,
                    steps,
                    self.size,
                    this_module["arg_a"]
                )
                self.size = a

                if self.context.multiprocessed:
                    self.image.pending["resize"] = [a]
                    offset = self.image.resize_by_ratio(
                        a, get_only_offset=True
                    )
                else:
                    offset = self.image.resize_by_ratio(
                        # If we're going to rotate, resize the rotated frame which is not the original image
                        a, from_current_frame="rotate" in modules
                    )

                if this_module["keep_center"]:
                    self.offset[0] += offset[0]
                    self.offset[1] += offset[1]

            if "blur" in modules:

                this_module = modules["blur"]

                ammount = eval(this_module["activation"].replace("X", str(fftinfo["average_value"])))

                if self.context.multiprocessed:
                    self.image.pending["blur"] = [ammount]
                else:
                    self.image.gaussian_blur(ammount)
            
            if "fade" in modules:

                this_module = modules["fade"]
                
                fade = this_module["object"]
                
                if fade.current_step < fade.finish_steps:
                    t = this_module["interpolation"](
                        fade.start_percentage,  
                        fade.end_percentage,
                        self.current_step,
                        fade.finish_steps,
                        fade.current_step,
                        this_module["arg_a"]
                    )
                    if self.context.multiprocessed:
                        self.image.pending["fade"] = [t]
                    else:
                        self.image.transparency(t)
                    fade.current_step += 1
                else:
                    # TODO: Failsafe really necessary?
                    if self.context.multiprocessed:
                        self.image.pending["fade"] = [fade.end_percentage]
                    else:
                        self.image.transparency(fade.end_percentage)

        # Iterate through every position module
        for position in positions:
            
            # # Override modules

            # Move according to a Point (be stationary)
            if self.utils.is_matching_type([position], [Point]):
                # Atribute (x, y) to Point's x and y
                self.x = int(position.y)
                self.y = int(position.x)

            # Move according to a Line (interpolate current steps)
            if self.utils.is_matching_type([position], [Line]):

                # Where we start and end
                start_coordinate = position.start
                end_coordinate = position.end

                # Interpolate X coordinate on line
                self.x = this_animation["interpolation_x"](
                    start_coordinate[1],  
                    end_coordinate[1],
                    self.current_step,
                    steps,
                    self.x,
                    this_animation["interpolation_x_arg_a"]
                )

                # Interpolate Y coordinate on line
                self.y = this_animation["interpolation_y"](
                    start_coordinate[0],  
                    end_coordinate[0],
                    self.current_step,
                    steps,
                    self.y,
                    this_animation["interpolation_y_arg_a"]
                )
            
            # # Offset modules

            # Get next shake offset value
            if self.utils.is_matching_type([position], [Shake]):
                position.next()
                self.offset[0] += position.x
                self.offset[1] += position.y

        # Next step, end of loop
        self.current_step += 1
    
    # Blit this item on the canvas
    def blit(self, canvas):

        x = int(self.x + self.offset[1] + self.base_offset[1])
        y = int(self.y + self.offset[0] + self.base_offset[0])

        canvas.canvas.overlay_transparent(
            self.image.frame,
            y, x
        )

        # This is for trivia / future, how it used to work until overlay_transparent wasn't slow anymore
        # img = self.image
        # width, height, _ = img.frame.shape
        # canvas.canvas.copy_from(
        #     self.image.frame,
        #     canvas.canvas.frame,
        #     [0, 0],
        #     [x, y],
        #     [x + width - 1, y + height - 1]
        # )

    def resolve_pending(self):
        self.image.resolve_pending()