"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Menu bar refactor for main editor window

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
import logging

import dearpygui.dearpygui as dear


class mmvEditorExternalsUI:
    def __init__(self, Editor):
        self.Editor = Editor
    
    def Render(self):
        logging.info(f"[mmvEditorMenuBarUI.About] Show About window")

        w, h, W, H = 200, 200, *self.Editor.Context.WINDOW_SIZE

        with dear.window(popup=True, modal=True, no_move=True) as ExternalsWindow:
            self.Editor.AddImageWidget(path=self.Editor.LogoImage, size=imgsize)
            dear.add_text(f"Externals Manager", color = (0,255,0))
            
        dear.set_item_pos(item=ExternalsWindow, x=(W-w)/2, y=(H-h-imgsize/2)/2)
 