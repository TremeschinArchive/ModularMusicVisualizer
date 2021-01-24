"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Generate wallpapers, particles on the go (tm)
This is kinda old code which will be moved at some point

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

from PIL import Image
import numpy as np
import random
import skia


class PyGradienter:
    def __init__(self, mmv, **kwargs):
        self.mmv = mmv
        debug_prefix = "[PyGradienter.__init__]"

        # How much images to generate
        self.n_images = kwargs.get("n_images", 1)
        print(debug_prefix, f"Generate N=[{self.n_images}] images")

        # Resolution    
        self.width = kwargs["width"]
        self.height = kwargs["height"]

        # Output dir, make directory if doesn't exist
        self.output_dir = kwargs["output_dir"]
        self.mmv.utils.mkdir_dne(self.output_dir)

        # Skia / canvas we'll draw to
        self.skia = kwargs["skia"]
        self.canvas = self.skia.canvas

        self.mode = kwargs.get("mode", "particles")

    def run(self):
        if self.mode == "polygons":
            self.polygons()
        elif self.mode == "particles":
            self.particles()

    # Generates particles for MMV
    def particles(self):
        
        print(f"Saving generated particle N=[", end="", flush=True)
        
        # Repeat for N images
        for i in range(self.n_images):

            # Reset canvas to transparent
            self.skia.reset_canvas()

            # How much nodes of gradients in this particle
            npoints = random.randint(1, 6)

            # Random scalars for each node, plus ending at zero
            scalars = [random.uniform(0.2, 1) for _ in range(npoints)] + [0]

            # Colors list
            colors = []

            # Iterate in decreasing order
            for scalar in reversed(sorted(scalars)):
                colors.append(skia.Color4f(1, 1, 1, scalar))
            
            # Create the skia paint with a circle at the center that ends on the edge
            paint = skia.Paint(
                Shader = skia.GradientShader.MakeRadial(
                    center = (self.width/2, self.height/2),
                    radius = self.width/2,
                    colors = colors,
                )
            )

            # Draw the particles
            self.canvas.drawPaint(paint)

            # # Save the image

            # Get the PIL image from the array of the canvas
            img = Image.fromarray(self.skia.canvas_array())

            # Pretty print
            if not i == self.n_images - 1:
                print(f"{i}, ", end = "", flush = True)   
            else:
                print(f"{i}]")

            # Save the particle to the output dir
            img.save(self.output_dir + f"/particle-{i}.png", quality = 100)

    def polygons(self):

        print(f"Saving generated polygons background N=[", end="", flush=True)
        
        BASE_GRADIENT_LINEAR = True
        MUTATION = True
        LOW_POLY = True
        RANDOM = True
        GREYSCALE = False

        for i in range(self.n_images):

            if BASE_GRADIENT_LINEAR:

                if RANDOM:
                    color1 = skia.Color4f(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
                    color2 = skia.Color4f(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)
                
                if GREYSCALE:
                    gradient1, gradient2 = random.uniform(0, 1), random.uniform(0, 1)
                    color1 = skia.Color4f(gradient1, gradient1, gradient1, 1)
                    color2 = skia.Color4f(gradient2, gradient2, gradient2, 1)

                paint = skia.Paint(
                    Shader = skia.GradientShader.MakeLinear(
                        points = [
                            (random.randint(-self.width/2, 0), random.randint(-self.height/2, 0)),
                            (self.width + random.randint(0, self.width/2), self.height + random.randint(0, self.height/2)) ],
                        colors = [color1, color2]
                    )
                )
                self.canvas.drawPaint(paint)
                colors = self.skia.canvas_array()
            

            if LOW_POLY:
                break_x = 20
                break_y = 15

                rectangle_widths = np.linspace(-self.width/4, 1.25*self.width, num = break_x)
                rectangle_heights = np.linspace(-self.height/4, 1.25*self.height, num = break_y)

                rectangle_width = self.width / break_x
                rectangle_height = self.height / break_y

                xx, yy = np.meshgrid(rectangle_widths, rectangle_heights)

                pairs = list(np.dstack([xx, yy]).reshape(-1, 2))

                if MUTATION:
                    for index in range(len(pairs)):
                        pairs[index][0] = pairs[index][0] + random.uniform(0, rectangle_width)
                        pairs[index][1] = pairs[index][1] + random.uniform(0, rectangle_height)
                
                # print(pairs)

                rectangle_points = []

                for index, point in enumerate(list(pairs)):
                    samerow = not ((index + 1) % break_x == 0)
                    # print(pairs[index], index, samerow)
                    try:
                        # If they are on the same height
                        if samerow:
                            rectangle_points.append([
                                list(pairs[index]),
                                list(pairs[index + break_x]),
                                list(pairs[index + break_x + 1]),
                                list(pairs[index + 1]),
                            ])   
                    except IndexError:
                        pass
                
                
                for rectangle in rectangle_points:
                    average_x = int(sum([val[0] for val in rectangle]) / 4)
                    average_y = int(sum([val[1] for val in rectangle]) / 4)

                    # print(rectangle, average_x, average_y)

                    rectangle_color = colors[min(max(average_y, 0), self.height - 1)][min(max(average_x, 0), self.width - 1)]
                    rectangle_color_fill = [x/255 for x in rectangle_color]
                    rectangle_color_border = [x/255 - 0.05 for x in rectangle_color]

                    # print(rectangle_color)

                    # Make a skia color with the colors list as argument
                    color = skia.Color4f(*rectangle_color_fill)

                    # Make the skia Paint and
                    paint = skia.Paint(
                        AntiAlias = True,
                        Color = color,
                        Style = skia.Paint.kFill_Style,
                        StrokeWidth = 2,
                    )

                    color = skia.Color4f(*rectangle_color_border)

                    border = skia.Paint(
                        AntiAlias = True,
                        Color = color,
                        Style = skia.Paint.kStroke_Style,
                        StrokeWidth = 1,
                        # ImageFilter=skia.ImageFilters.DropShadow(3, 3, 5, 5, color)
                    )

                    path = skia.Path()
                    path.moveTo(*rectangle[0])

                    rectangle.append(rectangle[0])

                    for point in rectangle:
                        path.lineTo(*point)

                    self.canvas.drawPath(path, paint)
                    self.canvas.drawPath(path, border)
                                

            # Save
            img = self.skia.canvas_array()
            
            # Pretty print
            if not i == self.n_images - 1:
                print(f"{i}, ", end = "", flush = True)   
            else:
                print(f"{i}]")

            img = Image.fromarray(img).convert('RGB')
            img.save(self.output_dir + f"/img{i}.jpg", quality = 100)
