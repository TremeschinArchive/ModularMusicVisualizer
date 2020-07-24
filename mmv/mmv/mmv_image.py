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

from mmv.common.interpolation import Interpolation
from mmv.mmv_visualizer import MMVVisualizer
from mmv.common.functions import Functions
from mmv.common.frame import Frame
from mmv.common.utils import Utils
from mmv.mmv_modifiers import *
import copy
import cv2
import os


class Configure():
    def __init__(self, mmvimage_object):
        self.object = mmvimage_object
        self.animation_index = 0
    
    def init_animation_layer(self):
        self.set_animation_empty_dictionary()
        self.set_this_animation_steps()
        self.set_animation_position_interpolation(axis="both")

    # # # [ Set Methods ] # # #

    def set_animation_empty_dictionary(self):
        self.object.path[self.animation_index] = {}
        self.object.path[self.animation_index]["position"] = []
        self.object.path[self.animation_index]["modules"] = {}
    
    def set_animation_position_interpolation(self, axis="both", method=None, arg_a=None):
        if axis == "both":
            for ax in ["x", "y"]:
                self.set_animation_position_interpolation(axis=ax)
        if not method in [None]:
            print("Unhandled interpolation method [%s]" % method)
            sys.exit(-1)
        
        self.object.path[self.animation_index]["interpolation_%s" % axis] = method
        self.object.path[self.animation_index]["interpolation_%s_arg_a" % axis] = arg_a

    def set_animation_index(self, n):
        self.animation_index = n

    def set_this_animation_steps(self, steps=math.inf):
        self.object.path[self.animation_index]["steps"] = steps

    # # # [ Next Methods ] # # #

    def next_animation_index(self):
        self.animation_index += 1
    
    # # # [ Add Methods ] # # #

    def add_path_point(self, x, y):
        self.object.path[self.animation_index]["position"].append(Point(x, y))

    def load_image(self, path):
        self.object.image.load_from_path(path, convert_to_png=True)

    def load_video(self, path):
        self.add_module_video(path)
    
    def resize_to_resolution(self, width, height, override=False):
        self.object.image.resize_to_resolution(int(width), int(height), override=override)
    
    def resize_to_video_resolution(self, over_resize_x=0, over_resize_y=0):
        self.resize_to_resolution(
            width=self.object.context.width + over_resize_x,
            height=self.object.context.height + over_resize_y,
            override=True
        )

    # # Generic add module

    def add_module(self, module):
        module_name = list(module.keys())[0]
        print("Adding module", module, module_name)
        self.object.path[self.animation_index]["modules"][module_name] = module[module_name]

    def add_module_blur(self, activation):
        self.add_module({
            "blur": { "activation": activation }
        })
    
    def add_module_glitch(self, activation, color_offset=False, scan_lines=False):
        self.add_module({
            "glitch": {
                "activation": activation,
                "color_offset": color_offset,
                "scan_lines": scan_lines,
            }
        })
    
    def add_module_video(self, path):
        self.add_module({
            "video": {
                "path": path
            }
        })
    
    def add_module_rotate(self, modifier):
        self.add_module({
            "rotate": {
                "object": modifier
            }
        })
    
    # Is this even python?
    def add_module_visualizer(self, 
                              vis_type,
                              vis_mode,
                              width, height,
                              minimum_bar_size,
                              activation_function,
                              activation_function_arg_a,
                              fourier_interpolation_function,
                              fourier_interpolation_activation,
                              fourier_interpolation_arg_a,
                              fourier_interpolation_steps,
                              pre_fft_smoothing, pos_fft_smoothing,
                              subdivide ):
        self.add_module({
            "visualizer": {
                "object": MMVVisualizer(
                    self.object.context,
                    {
                        "type": vis_type,
                        "mode": vis_mode,
                        "width": width,
                        "height": height,
                        "minimum_bar_size": minimum_bar_size,
                        "activation": {
                            "function": activation_function,
                            "arg_a": activation_function_arg_a,
                        },
                        "fourier": {
                            "interpolation": {
                                "function": fourier_interpolation_function,
                                "activation": fourier_interpolation_activation,
                                "arg_a": fourier_interpolation_arg_a,
                                "steps": fourier_interpolation_steps
                            },
                            "fitfourier": {
                                "pre_fft_smoothing": pre_fft_smoothing,
                                "pos_fft_smoothing": pos_fft_smoothing,
                                "subdivide": subdivide,
                            }
                        }
                    }
                )
            }
        })
    
    def add_resize_module(self, keep_center, interpolation, activation, smooth):
        self.add_module({
            "resize": {
                "keep_center": True,
                "interpolation": interpolation,
                "activation": activation,
                "arg_a": smooth,
            }
        })
    
    def add_vignetting_module(self, minimum, activation, center_function_x, center_function_y, start_value=0):
        self.add_module({
            "vignetting": {
                "object": Vignetting(
                    minimum = minimum,
                    activation = activation,
                    center_function_x = center_function_x,
                    center_function_y = center_function_y,
                    start_value=start_value,
                ),
                "interpolation": copy.deepcopy(self.object.interpolation.remaining_approach),
                "arg_a": 0.09,
            },
        })

    def simple_add_vignetting(self, intensity="medium", center="centered", activation=None, center_function_x=None, center_function_y=None, start_value=900):
        intensities = {
            "low": "0",
            "medium": "%s - 4000*X" % start_value,
            "high": "0",
            "custom": activation
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled resize intensity [%s]" % intensity)
            sys.exit(-1)

        if center == "centered":
            center_function_x = Constant(self.object.image.width // 2)
            center_function_y = Constant(self.object.image.height // 2)

        self.add_vignetting_module(
            minimum = 450,
            activation = intensities[intensity],
            center_function_x = center_function_x,
            center_function_y = center_function_y,
            start_value=start_value,
        )

    # Pre defined simple modules

    def simple_add_visualizer_circle(self, minimum_bar_size, width, height, mode="symetric", responsiveness=0.25, pre_fft_smoothing=2, pos_fft_smoothing=0, subdivide=2):
        self.add_module_visualizer(
            vis_type="circle", vis_mode=mode,
            width=width, height=height,
            minimum_bar_size=minimum_bar_size,
            activation_function=copy.deepcopy(self.object.functions.sigmoid),
            activation_function_arg_a=10,
            fourier_interpolation_function=copy.deepcopy(self.object.interpolation.remaining_approach),
            fourier_interpolation_activation="X",
            fourier_interpolation_arg_a=responsiveness,
            fourier_interpolation_steps=math.inf,
            pre_fft_smoothing=pre_fft_smoothing,
            pos_fft_smoothing=pos_fft_smoothing,
            subdivide=subdivide
        )
    
    def simple_add_path_modifier_shake(self, shake_max_distance, x_smoothness=0.01, y_smoothness=0.02):
        self.object.path[self.animation_index]["position"].append(
            Shake({
                "interpolation_x": copy.deepcopy(self.object.interpolation.remaining_approach),
                "interpolation_y": copy.deepcopy(self.object.interpolation.remaining_approach),
                "x_steps": "end_interpolation", "y_steps": "end_interpolation",
                "distance": shake_max_distance,
                "arg_a": x_smoothness,
                "arg_b": y_smoothness,
            })
        )
    
    def simple_add_linear_blur(self, intensity="medium"):
        intensities = {
            "low": "10*X",
            "medium": "15*X",
            "high": "20*X",
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled blur intensity [%s]" % intensity)
            sys.exit(-1)
            
        self.add_module_blur(intensities[intensity])
    
    def simple_add_glitch(self, intensity="medium", color_offset=False, scan_lines=False):
        intensities = {
            "low": "10*X",
            "medium": "15*X",
            "high": "20*X",
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled blur intensity [%s]" % intensity)
            sys.exit(-1)
            
        self.add_module_glitch(
            activation = intensities[intensity],
            color_offset = color_offset,
            scan_lines = scan_lines
        )
    
    def simple_add_linear_resize(self, intensity="medium", smooth=0.08, activation=None):
        intensities = {
            "low": "1 + 0.5*X",
            "medium": "1 + 2.5*X",
            "high": "1 + 4*X",
            "custom": activation
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled resize intensity [%s]" % intensity)
            sys.exit(-1)

        self.add_resize_module(
            keep_center=True,
            interpolation=copy.deepcopy(self.object.interpolation.remaining_approach),
            activation=intensities[intensity],
            smooth=smooth
        )
    
    def simple_add_swing_rotation(self, max_angle=6, smooth=100):
        self.add_module_rotate( SineSwing(max_angle, smooth) )
    
    def simple_add_linear_rotation(self, smooth=10):
        self.add_module_rotate( LinearSwing(smooth) )


class MMVImage():
    def __init__(self, context):
        
        debug_prefix = "[MMVImage.__init__]"
        
        self.context = context

        self.path = {}

        self.interpolation = Interpolation()
        self.configure = Configure(self)
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
    
    # Out Canvas is an MMVImage object
    def create_canvas(self):
        self.configure.init_animation_layer()
        self.reset_canvas()
        self.configure.add_path_point(0, 0)
    
    def reset_canvas(self):
        self.image.new(self.context.width, self.context.height, transparent=True)

    # Don't pickle cv2 video  
    def __getstate__(self):
        state = self.__dict__.copy()
        if "video" in state:
            del state["video"]
        return state
    
    # Next step of animation
    def next(self, fftinfo, this_step):

        self.current_step += 1

        # Animation has ended, this current_animation isn't present on path.keys
        if not self.current_animation in list(self.path.keys()):
            self.is_deletable = True
            return

        # The animation we're currently playing
        this_animation = self.path[self.current_animation]

        # The current step is one above the steps we've been told, next animation
        if self.current_step == this_animation["steps"] + 1:
            self.current_animation += 1
            self.current_step = 0
            return
        
        # Reset offset, pending
        self.offset = [0, 0]
        self.image.pending = {}

        self.image._reset_to_original_image()

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

                shake = 0

                for position in positions:
                    if self.utils.is_matching_type([position], [Shake]):
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
        
                amount = fftinfo["average_value"]

                if amount > 1:
                    amount = 1
                if amount < -0.9:
                    amount = -0.9

                amount = this_module["interpolation"](
                    self.size,
                    eval(this_module["activation"].replace("X", str(amount))),
                    self.current_step,
                    steps,
                    self.size,
                    this_module["arg_a"]
                )

                amount = round(amount, self.ROUND)
                self.size = amount

                if self.context.multiprocessed:
                    self.image.pending["resize"] = [amount]
                    offset = self.image.resize_by_ratio(
                        amount, get_only_offset=True
                    )
                else:
                    offset = self.image.resize_by_ratio(
                        # If we're going to rotate, resize the rotated frame which is not the original image
                        amount, from_current_frame="rotate" in modules
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
            
                amount = this_module["interpolation"](
                    fade.start_percentage,  
                    fade.end_percentage,
                    self.current_step,
                    fade.finish_steps,
                    fade.current_step,
                    this_module["arg_a"]
                )

                amount = round(amount, self.ROUND)

                if self.context.multiprocessed:
                    self.image.pending["transparency"] = [amount]
                else:
                    self.image.transparency(amount)
                    
                fade.current_step += 1
        
            # Apply vignetting
            if "vignetting" in modules:

                # The module we're working with
                this_module = modules["vignetting"]

                # TODO: needed?
                # Limit the average
                average = fftinfo["average_value"]

                if average > 1:
                    average = 1
                if average < -0.9:
                    average = -0.9

                vignetting = this_module["object"]

                # Where the vignetting intensity is pointing to according to our 
                vignetting.calculate_towards(
                    eval( vignetting.activation.replace("X", str(average)) )
                )

                # Interpolate to a new vignetting value
                next_vignetting = this_module["interpolation"](
                    vignetting.value,
                    vignetting.towards,
                    self.current_step,
                    steps,
                    vignetting.value,
                    this_module["arg_a"]
                )

                vignetting.value = next_vignetting

                vignetting.get_center()

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

    # Blit this item on the canvas
    def blit(self, canvas):

        x = int(self.x + self.offset[1])
        y = int(self.y + self.offset[0])

        canvas.image.overlay_transparent(
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

    def resolve_pending(self):
        self.image.resolve_pending()
