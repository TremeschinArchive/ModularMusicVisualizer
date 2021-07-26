"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

===============================================================================

Purpose: DearPyGui Utilities

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
from contextlib import contextmanager

import dearpygui.dearpygui as Dear
import numpy as np
from PIL import Image


# Log sender and data
def _log_sender_data(sender, app_data, user_data=None):
    logging.info(f"[Event Log] Sender: [{sender}] | App Data: [{app_data}] | User Data: [{user_data}]")

# Enter a DPG container Stack using "with", it pushes then pops after exiting
class EnterDearContainerStack:
    def __init__(self, DearID): Dear.push_container_stack(DearID)
    def __enter__(self): ...
    def __exit__(self, *args, **kwargs): Dear.pop_container_stack()

@contextmanager
def DearCenteredWindow(Context, **k):
    try:
        # Default values
        for item, value in [
            ("modal",True), ("no_move",True),
            ("autosize",True), ("label",""),
        ]:
            k[item] = k.get(item, value)

        # Add centered window
        window = Dear.add_window(**k)
        Dear.push_container_stack(window)
        Dear.set_item_pos(
            item=window,
            pos=[
                ( Context.DotMap.WINDOW_SIZE[0] - k.get("width", 0) - k.get("offx",0) ) / 2,
                Context.DotMap.CENTERED_WINDOWS_VERTICAL_DISTANCE,
            ])
        yield window
    finally: Dear.pop_container_stack()

def DearCenteredWindowsSuggestedMaxVSize(Context):
    return Context.DotMap.WINDOW_SIZE[1] - (2*Context.DotMap.CENTERED_WINDOWS_VERTICAL_DISTANCE)

# Adds a image on current DPG stack, returns the DPG dynamic texture
def DearAddDynamicTexture(FilePath, TextureRegistry, size=100) -> np.ndarray:
    img = Image.open(FilePath).convert("RGBA")
    original_image_data = np.array(img)
    width, height = img.size
    ratio = width / height
    img = img.resize((int(size*ratio), int(size)), resample=Image.LANCZOS)
    width, height = img.size
    data = np.array(img).reshape(-1)
    tex = Dear.add_dynamic_texture(width, height, list(data/256), parent=TextureRegistry)
    return tex

# Wrapper for calling Dear.add_theme_color or Dear.add_theme_style inputting a string
def DearSetThemeString(Key, Value, Parent):
    target = Dear.__dict__[Key]
    if not isinstance(Value, list): Value = [Value]
    
    # Get category
    if   "Node" in Key: category = Dear.mvThemeCat_Nodes
    elif "Plot" in Key: category = Dear.mvThemeCat_Plot
    else:               category = Dear.mvThemeCat_Core

    if "Col_"      in Key: Dear.add_theme_color(target,  Value, category=category, parent=Parent)
    if "StyleVar_" in Key: Dear.add_theme_style(target, *Value, category=category, parent=Parent)


def DearAddFontRangeHints(Font):
    # Add all font ranges one would need, overkill? yes
    for FontRangeHint in [
        Dear.mvFontRangeHint_Japanese,
        Dear.mvFontRangeHint_Korean,
        # Dear.mvFontRangeHint_Chinese_Full,
        # Dear.mvFontRangeHint_Chinese_Simplified_Common,
        Dear.mvFontRangeHint_Cyrillic,  # Russian
        # Dear.mvFontRangeHint_Thai,
        # Dear.mvFontRangeHint_Vietnamese,
    ]:
        Dear.add_font_range_hint(FontRangeHint, parent=Font)
    
    # Hindi range
    Dear.add_font_range(0x0900, 0x097F, parent=Font)
    