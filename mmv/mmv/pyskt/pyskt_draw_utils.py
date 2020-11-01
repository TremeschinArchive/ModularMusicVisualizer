"""
===============================================================================

Purpose: Draw utilities for PySKT

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

import skia

class SkiaDrawUtils:
    def __init__(self, pyskt_main):
        self.pyskt_main = pyskt_main

    """
    Draws every text on list one below another at a certain (x, y) and anchor point

    kwargs:

    {
        "font": skia.Font(skia.Typeface('Arial'), 24),
        "paint": skia.Paint(AntiAlias=True, Color=skia.ColorWHITE)
    }

    Anchor is where the coordinate (x, y) is located on the text, ranges from 0 to 1
    Anchor of (0.5, 0.5) is centerd (half way through width and height), (1, 1) is bottom right
    """
    def anchored_text(self, canvas, text, x: int, y: int, anchor_x: float, anchor_y: float, **kwargs):
        
        # If user sent a single string, it means a 1 item list
        if not isinstance(text, list):
            text = [text]
        
        # Get paint, font
        paint = kwargs.get("paint", skia.Paint(AntiAlias=True, Color=skia.ColorWHITE))
        font = kwargs.get("font", skia.Font(skia.Typeface('Arial'), 24))
        
        # Width and height of text
        height_size = font.getSpacing()

        for line_number, text_string in enumerate(text):

            text_size = font.measureText(text_string)

            # Where we'll plot the top left text according to the anchor and whatnot
            real_x = x - (text_size * anchor_x)
            real_y = y - (height_size * anchor_y) + height_size + (line_number * height_size)

            canvas.drawString(text_string, real_x, real_y, font, paint)


""" 

            
# bold_typeface = skia.Typeface('Arial', skia.FontStyle.Bold())
# italic_typeface = skia.Typeface('Arial', skia.FontStyle.Italic())
# print(bold_typeface)
# print(italic_typeface)

# font = skia.Font(skia.Typeface('Times New Roman'), 24)
# print(font)


center_x = width/2
center_y = height/2

c = skia.Color4f(1, 0, 1, 0.3)


for _ in range(30):
    # Rectangle border
    border = skia.Rect(
        random.randint(0, width),
        random.randint(0, height),
        random.randint(0, width),
        random.randint(0, height),
    )
    
    # Draw the border
    canvas.drawRect(border, paint)
"""