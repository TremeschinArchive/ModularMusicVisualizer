"""
===============================================================================

Purpose: Generate wallpapers, particles on the go (tm)

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

    def run(self):
        self.polygons()
    

    def polygons(self):

        BASE_GRADIENT_LINEAR = True
        MUTATION = True
        LOW_POLY = True

        for i in range(self.n_images):

            if BASE_GRADIENT_LINEAR:
                paint = skia.Paint(
                    Shader = skia.GradientShader.MakeLinear(
                        points = [
                            (random.randint(-self.width/2, 0), random.randint(-self.height/2, 0)),
                            (self.width + random.randint(0, self.width/2), self.height + random.randint(0, self.height/2)) ],
                        colors = [
                            skia.Color4f(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1),
                            skia.Color4f(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1),
                        ]
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
                        StrokeWidth = 2,
                        # ImageFilter=skia.ImageFilters.DropShadow(3, 3, 5, 5, color)
                    )

                    path = skia.Path()
                    path.moveTo(*rectangle[0])

                    rectangle.append(rectangle[0])

                    for point in rectangle:
                        path.lineTo(*point)

                    self.canvas.drawPath(path, paint)
                    # self.canvas.drawPath(path, border)
                                

            # Save
            img = self.skia.canvas_array()
            print(f"save image n={i}")
            img = Image.fromarray(img).convert('RGB')
            img.save(self.output_dir + f"/img{i}.jpg", quality = 100)
