"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMV objects generators

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

from mmv.mmvskia.mmv_skia_modifiers import MMVSkiaModifierMode, MMVSkiaModifierLine, MMVSkiaModifierPoint, MMVSkiaModifierShake, MMVSkiaModifierFade
from mmv.mmvskia.mmv_skia_interpolation import MMVSkiaInterpolation
from mmv.mmvskia.mmv_skia_image import MMVSkiaImage
from mmv.common.cmn_utils import Utils
import random
import copy
import math
import os


class MMVSkiaParticleGenerator:
    def __init__(self, mmvskia_main, **kwargs):
        debug_prefix = "[MMVSkiaParticleGenerator.__init__]"
        self.mmvskia_main = mmvskia_main
        self.type = "mmvgenerator"
        self.is_deletable = False

        # # Configs on kwargs

        # Get preset
        preset = kwargs.get("preset", None)

        """
        NOTE: Those are relative to a 60 frames per second video and 720p resolution
    
        The preset is set via the "preset" kwarg
    
                [ GLOBAL CONFIGS ]
        {
            "particles_images_directory": str
                Randomly load an image from this directory and use it as a particle

            "add_per_step": float, (10), see presets
                Whenever this percentage hits 100, we create a particle.
                How much to add on each step?
                Some presets might override this default value

            "average_sound_amplitude_add_per_step": float, 40
                Multiply average audio amplitude by this scalar and add to progression until next particle
                Remember that the audio amplitude on a highly compressed audio should not exceed 0.5 unless heavy DC bias

            "layer: int, 3
                What layer on MMVSkiaAnimation to add the particles on?

            "do_apply_shake": bool, True
                Add shake modifier to particle?
                
                "shake_max_distance": int, 18
                    Maximum pixels distance the particle can shake

                "shake_x_rationess": float, 0.01
                "shake_y_rationess": float, 0.04
                    Remaining approach interpolation smoothness, higher = faster


            "do_apply_fade": bool, True
                Add Fade modifier to particle?
                See fade values of the presets
                
            "particle_minimum_size": float, 0.05
            "particle_maximum_size": float, 0.15
                Resize the original image resolution of the particle by this scalar, overrides
    
        }
    
                [ PRESETS CONFIGS ]
    

        - Bottom mid top: 
        
            Particles grow from below, stop at middle screen for a moment, runs and fades out upwards
        
        kwargs config:
            {
                "fade_values": list, [start, mid, end, random], [0, 0.7, 0, 0.2]
                    Start fade on "start", middle screen we're "mid" and end in "end" fade value
                    "random" is added or subtracted (-random, +random) from mid value

                "fade_total_step": int, 60
                    How much steps to finish the fade (both fades)?

                "x_interpolation_agressive": float, 0.04
                "y_interpolation_agressive": float, 0.04
                    The ratio of the remaining approach interpolation on each axis
            }
        

        - Middle out:

            Particles start from the middle of the screen and diverges from its origin
        
            OVERRIDDEN:
                add_per_step: 30

        kwargs config:
            {
                "fade_values": list, [start, end, random], [0.8, 0, 0.2]
                    Start fade on "start", end on end
                    "random" is added or subtracted (-random, +random) from start value
                
                "fade_total_step": int, 60
                    How much steps to finish the fade?

                "x_interpolation_agressive": float, 0.015
                "y_interpolation_agressive": float, 0.015
                    The ratio of the remaining approach interpolation on each axis
            }

        """

        # # Global Variables

        self.particles_images_directory = kwargs.get("particles_images_directory", None)
        self.next_particle_percentage = 0

        # Steps, layer
        self.add_per_step = kwargs.get("add_per_step", 10)
        self.add_to_layer = kwargs.get("layer", 3)
        self.average_sound_amplitude_add_per_step = kwargs.get("average_sound_amplitude_add_per_step", 40)

        # Shake
        self.do_apply_shake = kwargs.get("do_apply_shake", True)
        self.shake_max_distance = kwargs.get("shake_max_distance", 18)
        self.shake_x_rationess = kwargs.get("self.shake_x_rationess", 0.01)
        self.shake_y_rationess = kwargs.get("self.shake_y_rationess", 0.04)

        # Fade
        self.do_apply_fade = kwargs.get("do_apply_fade", True)

        # Size
        self.particle_minimum_size = kwargs.get("particle_minimum_size", 0.05)
        self.particle_maximum_size = kwargs.get("particle_maximum_size", 0.15)

        # # Presets specifics

        # Bottom mid top configs
        if preset == "bottom_mid_top":

            # Set the function to generate the particles themselves
            self.generate_function = self.preset_bottom_mid_top

            # Fade
            self.fade_values = kwargs.get("fade_values", [0, 0.7, 0, 0.2])
            self.fade_start = self.fade_values[0]
            self.fade_mid = self.fade_values[1]
            self.fade_end = self.fade_values[2]
            self.fade_random = self.fade_values[3]
            self.fade_total_step = kwargs.get("fade_total_step", 60)

            # Path interpolation
            self.x_interpolation_agressive = kwargs.get("x_interpolation_agressive", 0.04)
            self.y_interpolation_agressive = kwargs.get("y_interpolation_agressive", 0.04)
        
        # Middle out configs
        elif preset == "middle_out":
            
            # Set the function to generate the particles themselves
            self.generate_function = self.preset_middle_out

            # Fade
            self.fade_values = kwargs.get("fade_values", [0.8, 0, 0.2])
            self.fade_start = self.fade_values[0]
            self.fade_end = self.fade_values[1]
            self.fade_random = self.fade_values[2]
            self.fade_total_step = kwargs.get("fade_total_step", 60)

            # Path
            self.x_interpolation_agressive = kwargs.get("x_interpolation_agressive", 0.015)
            self.y_interpolation_agressive = kwargs.get("y_interpolation_agressive", 0.015)

            # This preset requires more particles than the bottom mid top to look cool
            self.add_per_step = kwargs.get("add_per_step", 30)

        else:
            raise RuntimeError("No valid generator preset set")

        # # Error checking
        
        # Particles directory
        assert (self.particles_images_directory is not None), "Didn't set a particles directory"
        assert (os.path.exists(self.particles_images_directory)), "Particles directory not valid or doesn't exist"
        assert (len(os.listdir(self.particles_images_directory)) > 0), "Particles directory is empty"

    # Next function called from MMVAnimation
    def next(self):
        
        # Add progression until new generated object
        self.next_particle_percentage += self.add_per_step * self.mmvskia_main.context.fps_ratio_multiplier

        # Add more progression on particles according to sound level
        self.next_particle_percentage += self.average_sound_amplitude_add_per_step * self.mmvskia_main.core.modulators["average_value"]

        generate_amount = int(self.next_particle_percentage / 100)

        # No particles to generate
        if generate_amount == 0:
            return [{"object": None}]

        # The list of stuff we'll append on this step
        next_items = []

        # Loop generate_amount times
        for _ in range(generate_amount):
            
            # Subtract one full item generated
            self.next_particle_percentage -= 100

            # Call and append new stuff on the next_items list
            next_items.append({
                "object": self.generate_function(),
                "layer": self.add_to_layer
            })
        
        return next_items
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # Bottom mid top preset generator function
    def preset_bottom_mid_top(self):

        particle = MMVSkiaImage(mmvskia_main = self.mmvskia_main, from_generator = True)

        # Load random particle
        particle.image.load_from_path(
            self.mmvskia_main.utils.random_file_from_dir (
                self.particles_images_directory, silent = True
            )
        )
        
        horizontal_randomness = int(50 * self.mmvskia_main.context.resolution_ratio_multiplier)
        vertical_randomness_min = self.mmvskia_main.context.height//1.7
        vertical_randomness_max = self.mmvskia_main.context.height//2.3

        # # Create start, mid, end positions

        x1 = random.randint(0, self.mmvskia_main.context.width)
        y1 = self.mmvskia_main.context.height
        x2 = x1 + random.randint(-horizontal_randomness, horizontal_randomness)
        y2 = y1 + random.randint(-vertical_randomness_min, -vertical_randomness_max)
        x3 = x2 + random.randint(-horizontal_randomness, horizontal_randomness)
        y3 = y2 + random.randint(-vertical_randomness_min, -vertical_randomness_max)

        # # 

        # Empty path and modules
        path = []
        modules = {}

        line_path = MMVSkiaModifierLine(
            self.mmvskia_main,
            start = (x1, y1),
            end = (x2, y2),
            interpolation_x = MMVSkiaInterpolation(
                self.mmvskia_main,
                function = "remaining_approach",
                ratio = self.x_interpolation_agressive,
            ),
            interpolation_y = MMVSkiaInterpolation(
                self.mmvskia_main,
                function = "remaining_approach",
                ratio = self.y_interpolation_agressive,
            ),
            mode = MMVSkiaModifierMode.OVERRIDE_VALUE_RESET_OFFSET,
        )

        # Add line path (required)
        path.append(line_path)
        
        # Create and append shake modifier if set
        if self.do_apply_shake:
            shake_path = MMVSkiaModifierShake(
                self.mmvskia_main,
                interpolation_x = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = self.shake_x_rationess,
                    start = 0,
                ),
                interpolation_y = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = self.shake_y_rationess,
                    start = 0,
                ),
                distance = self.shake_max_distance,
                mode = MMVSkiaModifierMode.OFFSET_VALUE,
            )
            path.append(shake_path)

        # Add Fade module if set
        if self.do_apply_fade:
            
            # Add random number to fade mid
            self.fade_mid += random.uniform(-self.fade_random, self.fade_random)

            # Upper and lower limit fade mid value
            self.fade_mid = max(min(self.fade_mid, 1), 0)

            # Create Fade module
            modules["fade"] = {
                "object": MMVSkiaModifierFade(
                    self.mmvskia_main,
                    interpolation = MMVSkiaInterpolation(
                        self.mmvskia_main,
                        function = "linear",
                        total_steps = self.fade_total_step,
                        start = self.fade_start,
                        end = self.fade_mid,
                    )
                )
            }

        this_steps = random.randint(50, 100)

        # First path of animation, we go to the middle of the screen
        particle.animation[0] = {
            "position": {
                "path": path,
            },
            "animation": {
                "steps": this_steps,
            },
            "modules": modules
        }

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        path = []
        modules = {}

        line_path = MMVSkiaModifierLine(
            self.mmvskia_main,
            start = (x2, y2),
            end = (x3, y3),
            interpolation_x = MMVSkiaInterpolation(
                self.mmvskia_main,
                function = "remaining_approach",
                ratio = self.x_interpolation_agressive,
            ),
            interpolation_y = MMVSkiaInterpolation(
                self.mmvskia_main,
                function = "remaining_approach",
                ratio = self.y_interpolation_agressive,
            ),
            mode = MMVSkiaModifierMode.OVERRIDE_VALUE_RESET_OFFSET,
        )
       
        # Add line path (required)
        path.append(line_path)

        # Add the same Shake modifier
        if self.do_apply_shake:
            path.append(shake_path)

        # Add post mid screen Fade        
        if self.do_apply_fade:
            modules["fade"] = {
                "object": MMVSkiaModifierFade(
                    self.mmvskia_main,
                    interpolation = MMVSkiaInterpolation(
                        self.mmvskia_main,
                        function = "linear",
                        total_steps = self.fade_total_step,
                        start = self.fade_mid,
                        end = self.fade_end,
                    )
                )
            }
        
        this_steps = random.randint(150, 200)

        # Second layer of animation, go up and (fade out?)
        particle.animation[1] = {
            "position": {
                "path": path,
            },
            "animation": {
                "steps": this_steps
            },
            "modules": modules
        }

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        # Resize the image by a scalar
        particle.image.resize_by_ratio(
            random.uniform(
                self.particle_minimum_size * self.mmvskia_main.context.resolution_ratio_multiplier,
                self.particle_maximum_size * self.mmvskia_main.context.resolution_ratio_multiplier,
            ),
            override=True
        )

        return particle


    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


    def preset_middle_out(self):

        particle = MMVSkiaImage(mmvskia_main = self.mmvskia_main, from_generator = True)

        # Load random particle
        particle.image.load_from_path(
            self.mmvskia_main.utils.random_file_from_dir (
                self.particles_images_directory, silent = True
            )
        )
        
        # #  Create start and end positions

        # We start at half the screen
        x1 = self.mmvskia_main.context.width // 2
        y1 = self.mmvskia_main.context.height // 2

        # The minimum distance we'll walk is the diagonal (Center - Corner) * minimum_distance_ratio
        # The maximum distance we'll walk is the diagonal (Center - Corner) * maximum_distance_ratio
        self.mmvskia_main.polar_coordinates.from_r_theta(
            r = self.mmvskia_main.context.resolution_diagonal / 2,
            theta = random.uniform(0, 2*math.pi),
        )

        # The direction we'll walk..
        walk_to = self.mmvskia_main.polar_coordinates.get_rectangular_coordinates()

        # Is where we're at plus that
        x2 = x1 + walk_to[0]
        y2 = y1 + walk_to[1]

        # # 

        # Empty path and modules
        path = []
        modules = {}

        # Line path going from the center
        line_path = MMVSkiaModifierLine(
            self.mmvskia_main,
            start = (x1, y1),
            end = (x2, y2),
            interpolation_x = MMVSkiaInterpolation(
                self.mmvskia_main,
                function = "remaining_approach",
                ratio = self.x_interpolation_agressive,
                speed_up_by_audio_volume = 0.3,
            ),
            interpolation_y = MMVSkiaInterpolation(
                self.mmvskia_main,
                function = "remaining_approach",
                ratio = self.y_interpolation_agressive,
                speed_up_by_audio_volume = 0.3,
            ),
            mode = MMVSkiaModifierMode.OVERRIDE_VALUE_RESET_OFFSET,
        )

        # Add line path (required)
        path.append(line_path)

        # Create and append shake modifier if set
        if self.do_apply_shake:
            shake_path = MMVSkiaModifierShake(
                self.mmvskia_main,
                interpolation_x = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = 0.01,
                    start = 0,
                ),
                interpolation_y = MMVSkiaInterpolation(
                    self.mmvskia_main,
                    function = "remaining_approach",
                    ratio = 0.04,
                    start = 0,
                ),
                distance = 18,
                mode = MMVSkiaModifierMode.OFFSET_VALUE,
            )
            path.append(shake_path)

        # Set fade    
        if self.do_apply_fade:
            # Create Fade module with random number to start of the fade
            modules["fade"] = {
                "object": MMVSkiaModifierFade(
                    self.mmvskia_main,
                    interpolation = MMVSkiaInterpolation(
                        self.mmvskia_main,
                        function = "linear",
                        total_steps = self.fade_total_step,
                        start = self.fade_start + random.uniform(-self.fade_random, self.fade_random),
                        end = self.fade_end,
                    )
                )
            }

        this_steps = random.randint(50, 100)

        # Set the animation
        particle.animation[0] = {
            "position": {
                "path": path,
            },
            "animation": {
                "steps": this_steps,
            },
            "modules": modules,
        }
        
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

        # Resize the image by a scalar
        particle.image.resize_by_ratio(
            random.uniform(
                self.particle_minimum_size * self.mmvskia_main.context.resolution_ratio_multiplier,
                self.particle_maximum_size * self.mmvskia_main.context.resolution_ratio_multiplier,
            ),
            override=True
        )

        return particle
