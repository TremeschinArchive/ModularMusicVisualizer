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

from mmv.mmv_interpolation import MMVInterpolation
from mmv.common.cmn_functions import Functions
from mmv.mmv_visualizer import MMVVisualizer
from mmv.common.cmn_frame import Frame
from mmv.common.cmn_utils import Utils
from mmv.mmv_context import Context
from mmv.common.cmn_types import *
from mmv.mmv_modifiers import *
from typing import Union
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

                amount = this_module["interpolation"].next()
            
                amount = round(amount, self.ROUND)
                print("trans", amount)

                if self.context.multiprocessed:
                    self.image.pending["transparency"] = [amount]
                else:
                    self.image.transparency(amount)
                    
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
        for modifier in path:
            
            # # Override modules

            # Move according to a Point (be stationary)
            if self.utils.is_matching_type([modifier], [Point]):
                # Atribute (x, y) to Point's x and y
                self.x = int(modifier.y)
                self.y = int(modifier.x)

            # Move according to a Line (interpolate current steps)
            if self.utils.is_matching_type([modifier], [Line]):

                # Where we start and end
                start_coordinate = modifier.start
                end_coordinate = modifier.end

                modifier.next()

                # Interpolate X coordinate on line
                self.x = modifier.interpolation_x.current_value

                # Interpolate Y coordinate on line
                self.y = modifier.interpolation_y.current_value
            
            # # Offset modules

            # Get next shake offset value
            if self.utils.is_matching_type([modifier], [Shake]):
                modifier.next()
                self.offset[0] += modifier.x
                self.offset[1] += modifier.y

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


"""
NOTE: The activation functions where a str is expected, it just evaluates
that expression and replaces "X" (capital letter x) with the average autio
amplitude at that point.

This will be documented properly in the future (I hope so)
"""

# Configure our main MMVImage, wrapper around animations
class Configure:

    # Get MMVImage object and set image index to zero
    def __init__(self, mmvimage_object: MMVImage) -> None:
        self.object = mmvimage_object
        self.animation_index = 0
    
    # Macros for initialializing this animation layer
    def init_animation_layer(self) -> None:
        self.set_animation_empty_dictionary()
        self.set_this_animation_steps()
        self.set_animation_position_interpolation(axis="both")
    
    # # # [ Load Methods ] # # #

    def load_image(self, path: str) -> None:
        self.object.image.load_from_path(path, convert_to_png=True)

    def load_video(self, path: str) -> None:
        self.add_module_video(path)

    # # # [ Resize Methods ] # # #

    def resize_to_resolution(self,
            width: Union[int, float],
            height: Union[int, float],
            override: bool=False
        ) -> None:

        self.object.image.resize_to_resolution(int(width), int(height), override=override)
    
    def resize_to_video_resolution(self, over_resize_x: int=0, over_resize_y: int=0) -> None:
        self.resize_to_resolution(
            width=self.object.context.width + over_resize_x,
            height=self.object.context.height + over_resize_y,
            override=True
        )

    # # # [ Set Methods ] # # #

    # Make an empty animation layer according to this animation index, dicitonaries
    def set_animation_empty_dictionary(self) -> None:
        self.object.animation[self.animation_index] = {}
        self.object.animation[self.animation_index]["position"] = {"path": []}
        self.object.animation[self.animation_index]["modules"] = {}
        self.object.animation[self.animation_index]["animation"] = {}
    
    # X and Y needs interpolation
    def set_animation_position_interpolation(self,
            axis: str="both",
            method=None,
            arg_a=None
        ) -> None:

        if axis == "both":
            for ax in ["x", "y"]:
                self.set_animation_position_interpolation(axis=ax)
        if not method in [None]:
            print("Unhandled interpolation method [%s]" % method)
            sys.exit(-1)
        
        self.object.animation[self.animation_index]["position"]["interpolation_%s" % axis] = method

    # Override current animation index we're working on into new index
    def set_animation_index(self, n: int) -> None:
        self.animation_index = n

    # How much steps in this animation
    def set_this_animation_steps(self, steps: float=math.inf) -> None:
        self.object.animation[self.animation_index]["animation"]["steps"] = steps

    # # # [ Next Methods ] # # #

    # Next animation index from the current one
    def next_animation_index(self) -> None:
        self.animation_index += 1
    
    # # # [ Add Methods ] # # #

    ## Generic add module ##
    def add_module(self, module: dict) -> None:
        module_name = list(module.keys())[0]
        print("Adding module", module, module_name)
        self.object.animation[self.animation_index]["modules"][module_name] = module[module_name]
    ## Generic add module ##

    # Add a Point modifier in the path
    def add_path_point(self, x: Union[int, float], y: Union[int, float]) -> None:
        self.object.animation[self.animation_index]["position"]["path"].append(Point(x, y))

    # TODO: Add path Line

    # Add a Gaussian Blur module, only need activation
    # Read comment at the beginning of this class
    def add_module_blur(self, activation: str) -> None:
        self.add_module({
            "blur": { "activation": activation }
        })
    
    # Add a glitch module
    def add_module_glitch(self,
            activation: str,
            color_offset: bool=False,
            scan_lines: bool=False
        ) -> None:

        self.add_module({
            "glitch": {
                "activation": activation,
                "color_offset": color_offset,
                "scan_lines": scan_lines,
            }
        })
    
    # Add a video module, be sure to match the FPS of both the outpu
    def add_module_video(self, path: str) -> None:
        self.add_module({
            "video": {
                "path": path
            }
        })
    
    # Add a rotate module with an modifier object with next function
    def add_module_rotate(self, modifier: Union[SineSwing, LinearSwing]) -> None:
        self.add_module({
            "rotate": {
                "object": modifier
            }
        })
    
    # Is this even python?
    def add_module_visualizer(self, 
            vis_type: str,
            vis_mode: str,
            width: int, height: int,
            minimum_bar_size: Number,
            activation_function,
            activation_function_arg_a: Number,
            fourier_interpolation_function,
            pre_fft_smoothing: int,
            pos_fft_smoothing: int,
            subdivide: int
        ) -> None:

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
    
    # Add resize by ratio module
    def add_module_resize(self,
            keep_center: bool,
            interpolation,
            activation: str,
        ) -> None:

        self.add_module({
            "resize": {
                "keep_center": True,
                "interpolation": interpolation,
                "activation": activation,
            }
        })
    
    # Add vignetting module with minimum values
    def add_module_vignetting(self,
            minimum: Number,
            activation: str,
            center_function_x,
            center_function_y,
            start_value=0
        ) -> None:

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


    # # # # [ Pre defined simple modules ] # # # #

    # Just add a vignetting module without much trouble with an intensity
    def simple_add_vignetting(self,
            intensity: str="medium",
            center: str="centered",
            activation: bool=None,
            center_function_x=None,
            center_function_y=None,
            start_value: Number=900
        ) -> None:

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

        self.add_module_vignetting(
            minimum = 450,
            activation = intensities[intensity],
            center_function_x = center_function_x,
            center_function_y = center_function_y,
            start_value=start_value,
        )

    # Add a visualizer module
    def simple_add_visualizer_circle(self,
            minimum_bar_size: Number,
            width: Number,
            height: Number,
            mode: str="symetric",
            responsiveness: Number=0.25,
            pre_fft_smoothing: int=2,
            pos_fft_smoothing: int=0,
            subdivide:int=2
        ) -> None:

        self.add_module_visualizer(
            vis_type = "circle", vis_mode = mode,
            width = width, height = height,
            minimum_bar_size = minimum_bar_size,
            activation_function = copy.deepcopy(self.object.functions.sigmoid),
            fourier_interpolation_function = MMVInterpolation({
                "function": "sigmoid",
                "smooth": responsiveness,
            }),
            pre_fft_smoothing = pre_fft_smoothing,
            pos_fft_smoothing = pos_fft_smoothing,
            subdivide = subdivide

            
        )
    
    # Add a shake modifier on the pathing
    def simple_add_path_modifier_shake(self,
            shake_max_distance: Number,
            x_smoothness: Number=0.01,
            y_smoothness: Number=0.02
        ) -> None:

        self.object.animation[self.animation_index]["position"]["path"].append(
            Shake({
                "interpolation_x": MMVInterpolation({
                    "function": "remaining_approach",
                    "aggressive": x_smoothness,
                }),
                "interpolation_y": MMVInterpolation({
                    "function": "remaining_approach",
                    "aggressive": y_smoothness,
                }),
                "distance": shake_max_distance,
            })
        )
    
    # Blur the object based on an activation function
    def simple_add_linear_blur(self,
            intensity: str="medium",
            custom: str=""
        ) -> None:

        intensities = {
            "low": "10*X",
            "medium": "15*X",
            "high": "20*X",
            "custom": custom
        }
        if not intensity in list(intensities.keys()):
            print("Unhandled blur intensity [%s]" % intensity)
            sys.exit(-1)
            
        self.add_module_blur(intensities[intensity])
    
    # Add simple glitch effect based on an activation function
    def simple_add_glitch(self,
            intensity: str="medium",
            color_offset: bool=False,
            scan_lines: bool=False
        ) -> None:

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
    
    # Add simple linear resize based on an activation function
    def simple_add_linear_resize(self,
            intensity: str="medium",
            smooth: Number=0.08,
            activation: bool=None
        ) -> None:

        intensities = {
            "low": "1 + 0.5*X",
            "medium": "1 + 2.5*X",
            "high": "1 + 4*X",
            "custom": activation
        }
        if not intensity in list(intensities.keys()):
            raise RuntimeError("Unhandled resize intensity [%s]" % intensity)

        self.add_module_resize(
            keep_center = True,
            interpolation = MMVInterpolation({
                "function": "remaining_approach",
                "aggressive": smooth,
            }),
            activation=intensities[intensity],
        )
    
    # Add simple swing rotation, go back and forth
    def simple_add_swing_rotation(self,
            max_angle: Number=6,
            smooth: Number=100
        ) -> None:

        self.add_module_rotate( SineSwing(max_angle, smooth) )
    
    # Rotate to one direction continuously
    def simple_add_linear_rotation(self, smooth: int=10) -> None:
        self.add_module_rotate( LinearSwing(smooth) )