"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: MMVSkiaMusicBarsCircle object

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

from mmv.common.cmn_coordinates import PolarCoordinates
from mmv.common.cmn_functions import Functions
import numpy as np
import math
import skia


class MMVSkiaMusicBarsCircle:
    # Documentation of kwargs of this class on mmv_skia_music_bar.py interface class
    def __init__(self, mmv, MMVSkiaVectorial, **kwargs):
        debug_prefix = "[MMVSkiaMusicBarsCircle.__init__]"
        self.mmv = mmv
        self.vectorial = MMVSkiaVectorial

        # Utilities for calculating the bars positions
        self.polar = PolarCoordinates()

        # # Configs

        self.center_x = kwargs.get("center_x", "center")
        self.center_y = kwargs.get("center_y", "center")

        # If any of those center_* are set to "center", set them to half the screen width and height
        self.center_x = (self.mmv.context.width  / 2) if (self.center_x == "center") else (self.center_x)
        self.center_y = (self.mmv.context.height / 2) if (self.center_y == "center") else (self.center_y)
        print(debug_prefix, f"Bars center are [{self.center_x=}] [{self.center_y=}]")

        # The starting point  of the minimum bar size, optimal set to the logo circle radius
        self.minimum_bar_size = kwargs["minimum_bar_size"]
        print(debug_prefix, f"Minimum bar size is: [{self.minimum_bar_size}]")

        # The starting point  of the minimum bar size, optimal set to the logo circle radius
        self.maximum_bar_size = kwargs.get("maximum_bar_size", math.inf)
        print(debug_prefix, f"Maximum bar size is: [{self.maximum_bar_size}]")

        # Where the bar starts from
        self.bar_starts_from = kwargs.get("bar_starts_from", "center")
        print(debug_prefix, f"Bars will start from: [{self.bar_starts_from}]")

        # Multiply bar default size by this much
        self.bar_magnitude_multiplier = kwargs.get("bar_magnitude_multiplier", 1)

        # Increase stroke width of the bars based on the magnitude? if yes by how much
        self.bigger_bars_on_magnitude = kwargs.get("bigger_bars_on_magnitude", True)

        # If it is true then get its ratio
        if self.bigger_bars_on_magnitude:
            self.bigger_bars_on_magnitude_add_magnitude_divided_by = kwargs.get("bigger_bars_on_magnitude_add_magnitude_divided_by", 64)
            print(debug_prefix, f"Bars will get bigger based on magnitude, ratio: [magnitude/{self.bigger_bars_on_magnitude_add_magnitude_divided_by}]")
        else:
            print(debug_prefix, f"Bars will not get bigger based on magnitude")

        # The FFT does not reflect volume (in a linear way), more like a power density spectrum
        # So to have a more linear thingy (I honestly don't know the proper math to flatten it out)
        # I just multiply based on the frequency, magnitude times a scalar.
        #
        # 20  Hz - fft_20hz_multiplier
        # 20 kHz - fft_20khz_multiplier
        #
        # See that this forms two points and a line
        # A = (20, fft_20hz_multiplier) and B = (20k, fft_20khz_multiplier)
        self.fft_20hz_multiplier = kwargs.get("fft_20hz_multiplier", 0.8)
        self.fft_20khz_multiplier = kwargs.get("fft_20khz_multiplier", 12)
        print(debug_prefix, f"Points A=(20, {self.fft_20hz_multiplier}) B=(20 000, {self.fft_20khz_multiplier}) with X=frequency and Y=scalar will multiply the magnitudes")

        # Color preset
        self.color_preset = kwargs.get("color_preset", "colorful")
        print(debug_prefix, f"Using color preset: [{self.color_preset}]")

        # Settings for the colorful colors preset
        if self.color_preset == "colorful":
            
            # As time goes on, rotate the colors? What speed? more is slower
            self.color_rotates = kwargs.get("color_rotates", True)
            self.color_rotate_speed = kwargs.get("color_rotate_speed", 100)
        
        elif self.color_preset == "white": pass  # TODO: make this "monochromatic" and get user value
        else:
            raise RuntimeError(debug_prefix, f"Invalid color preset: [{self.color_preset}]")

    # Construct and blit to the Skia Canvas
    def build(self, fitted_ffts: dict, frequencies: list, config: dict, effects):
        debug_prefix = "[MMVSkiaMusicBarsCircle.build]"

        # We first store the coordinates to draw and their respective paints, draw afterwards
        data = {}

        # # TODO: This code was originally set to have "linear" or "symmetric" modes, I think
        # # we should keep symmetric mode only, that's my opinion
        
        # Loop on both channels
        for channel in (["l", "r"]):

            # Init blank channel of list of coordinates and paints
            data[channel] = {
                "coordinates": [],
                "paints": [],
            }

            # The FFT of this channel from the dictionary
            this_channel_fft = fitted_ffts[channel]

            # Length of the FFT
            NFFT = len(this_channel_fft)

            # For each magnite of the FFT and their respective index
            for index, magnitude in enumerate(this_channel_fft):

                # This is symmetric, so half a rotation divided by how much bars
                # Remember we're in Radians, pi radians is 180 degrees (half an rotation)
                angle_between_two_bars = math.pi / NFFT

                # We have to start from half a distance between bars and end on a full rotation minus a bars distance
                # depending on the channel we're in
                if channel == "l":
                    theta = self.mmv.functions.value_on_line_of_two_points(
                        Xa = 0,
                        Ya = (math.pi/2) + (angle_between_two_bars/2),
                        Xb = NFFT,
                        Yb = (math.pi/2) + math.pi + (angle_between_two_bars/2),
                        get_x = index,
                    )
                    
                elif channel == "r":
                    theta = self.mmv.functions.value_on_line_of_two_points(
                        Xa = 0,
                        Ya = (math.pi/2) - (angle_between_two_bars/2),
                        Xb = NFFT,
                        Yb = (math.pi/2) - math.pi - (angle_between_two_bars/2),
                        get_x = index,
                    )

                # Scale the magnitude according to the resolution
                magnitude *= self.mmv.context.resolution_ratio_multiplier

                # Calculate our flatten scalar as explained previously                
                flatten_scalar = self.mmv.functions.value_on_line_of_two_points(
                    Xa = 20,
                    Ya = self.fft_20hz_multiplier,
                    Xb = 20000,
                    Yb = self.fft_20khz_multiplier,
                    get_x = frequencies[0][index]
                )

                # The actual size of the music bar
                size = (magnitude) * (flatten_scalar) * (self.bar_magnitude_multiplier)

                # Hard crop maximum limit
                if size > self.maximum_bar_size:
                    size = self.maximum_bar_size

                # We send an r, theta just in case we want to do something with it later on
                data[channel]["coordinates"].append([
                    (self.minimum_bar_size + size) * effects["size"],
                    theta,
                ])

                # If a bar has a high magnitude, set the stroke width to be higher
                if self.bigger_bars_on_magnitude:
                    
                    # Calculate how much to add
                    bigger_bars_on_magnitude = (magnitude / self.bigger_bars_on_magnitude_add_magnitude_divided_by)
                    
                    # Scale according to the resolution
                    bigger_bars_on_magnitude /= self.mmv.context.resolution_ratio_multiplier
                else:
                    bigger_bars_on_magnitude = 0
                    
                # # Coloring

                # Radial colors
                if self.color_preset == "colorful":

                    # Rotate the colors a bit on each step
                    color_shift_on_angle = theta 

                    if self.color_rotates:
                        color_shift_on_angle += (self.mmv.core.this_step / self.color_rotate_speed)

                    # Define the color of the bars
                    colors = [
                        abs( math.sin((color_shift_on_angle / 2)) ),
                        abs( math.sin((color_shift_on_angle + ((1/3)*2*math.pi)) / 2) ),
                        abs( math.sin((color_shift_on_angle + ((2/3)*2*math.pi)) / 2) ),
                    ] + [0.89] # not full opacity

                    # Make a skia color with the colors list as argument
                    color = skia.Color4f(*colors)

                    # Make the skia Paint and
                    this_bar_paint = skia.Paint(
                        AntiAlias = True,
                        Color = color,
                        Style = skia.Paint.kStroke_Style,
                        StrokeWidth = 8 * self.mmv.context.resolution_ratio_multiplier + bigger_bars_on_magnitude,
                    )

                if self.color_preset == "white":

                    # Define the color of the bars
                    colors = [1.0, 1.0, 1.0, 0.89]

                    # Make a skia color with the colors list as argument
                    color = skia.Color4f(*colors)

                    # Make the skia Paint and
                    this_bar_paint = skia.Paint(
                        AntiAlias = True,
                        Color = color,
                        Style = skia.Paint.kStroke_Style,
                        StrokeWidth = 8 * self.mmv.context.resolution_ratio_multiplier + bigger_bars_on_magnitude,
                    )

                # Store it on a list do draw in the end
                data[channel]["paints"].append(this_bar_paint)

        # Our list of coordinates and paints, invert the right channel for drawing the path in the right direction
        # Not reversing it will yield "symmetric" bars along the diagonal
        coordinates = data["l"]["coordinates"] + [x for x in reversed(data["r"]["coordinates"]) ]
        paints = data["l"]["paints"] + [x for x in reversed(data["r"]["paints"]) ]
    

        # # # # # # # # # # # # These two code blocks are deprecated, not sure if they'll be used in a config # # # # # # # # # # # #

        # Filled background
        if False: # self.config["draw_background"]

            path = skia.Path()
            white_background = skia.Paint(
                AntiAlias = True,
                Color = skia.ColorWHITE,
                Style = skia.Paint.kFill_Style,
                StrokeWidth = 3,
                ImageFilter=skia.ImageFilters.DropShadow(3, 3, 5, 5, skia.ColorBLACK),
                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.0)
            )

            more = 1.05

            self.polar.from_r_theta(coordinates[0][0] * more, coordinates[0][1])
            polar_offset = self.polar.get_rectangular_coordinates()

            path.moveTo(
                (self.center_x + polar_offset[0]),
                (self.center_y + polar_offset[1]),
            )

            for coord_index, coord in enumerate(coordinates):

                # TODO: implement this function in DataUtils for not repeating myself
                get_nearby = 4

                size_coordinates = len(coordinates)
                real_state = coordinates*3

                nearby_coordinates = real_state[
                    size_coordinates + (coord_index - get_nearby):
                    size_coordinates + (coord_index + get_nearby)
                ]

                # [0, 1, 2, 3, 4] --> weights=
                #  3  4  5, 4, 3

                n = len(nearby_coordinates)

                weights = [n - abs( (n / 2) - x) for x in range(n)]

                s = 0
                for index, item in enumerate(nearby_coordinates):
                    s += item[0] * weights[index]

                avg_coord = s / sum(weights)

                self.polar.from_r_theta(avg_coord * more, coord[1])

                polar_offset = self.polar.get_rectangular_coordinates()

                path.lineTo(
                    (self.center_x + polar_offset[0]),
                    (self.center_y + polar_offset[1]),
                )
            
            self.mmv.skia.canvas.drawPath(path, white_background)

        # Countour, stroke
        if False: # self.config["draw_black_border"]

            more = 2

            path = skia.Path()

            black_stroke = skia.Paint(
                AntiAlias = True,
                Color = skia.ColorWHITE,
                Style = skia.Paint.kStroke_Style,
                StrokeWidth = 6,
                ImageFilter=skia.ImageFilters.DropShadow(3, 3, 5, 5, skia.ColorWHITE),
                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 1.0)
            )

            for coord_index, coord in enumerate(coordinates):

                get_nearby = 10

                size_coordinates = len(coordinates)
                real_state = coordinates*3

                nearby_coordinates = real_state[
                    size_coordinates + (coord_index - get_nearby):
                    size_coordinates + (coord_index + get_nearby)
                ]

                n = len(nearby_coordinates)

                weights = [n - abs( (n / 2) - x) for x in range(n)]

                s = 0
                for index, item in enumerate(nearby_coordinates):
                    s += item[0] * weights[index]

                avg_coord = s / sum(weights)

                self.polar.from_r_theta(self.minimum_bar_size + ( (avg_coord - self.minimum_bar_size) * more), coord[1])
                polar_offset = self.polar.get_rectangular_coordinates()

                coords = [ (self.center_x + polar_offset[0]), (self.center_y + polar_offset[1]) ]

                if coord_index == 0:
                    path.moveTo(*coords)
                path.lineTo(*coords)
            
            self.mmv.skia.canvas.drawPath(path, black_stroke)

        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Draw the main bars according to their index and coordinate
        for index, coord in enumerate(coordinates):
            
            # Empty path for drawing the bars        
            path = skia.Path()

            # Move to wanted center
            if self.bar_starts_from == "center":
                path.moveTo(self.center_x, self.center_y)

            # Move to the last bar end position
            elif self.bar_starts_from == "last":
                self.polar.from_r_theta(coordinates[index - 1][0], coordinates[index - 1][1])
                polar_offset = self.polar.get_rectangular_coordinates()
                path.moveTo(self.center_x + polar_offset[0], self.center_y + polar_offset[1])
            
            else:
                raise RuntimeError(debug_prefix, f"Invalid bar_starts_from: [{self.bar_starts_from}]")

            # Get a polar coordinate point, convert to rectangular
            self.polar.from_r_theta(coord[0], coord[1])
            polar_offset = self.polar.get_rectangular_coordinates()

            # Move to the final desired point
            path.lineTo(
                self.center_x + polar_offset[0],
                self.center_y + polar_offset[1],
            )

            # Draw the path according to its index's paint
            self.mmv.skia.canvas.drawPath(path, paints[index])
