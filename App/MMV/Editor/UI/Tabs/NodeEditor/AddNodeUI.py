"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021, Tremeschin

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
import dearpygui.dearpygui as Dear
from MMV.Common.DearPyGuiUtils import *
from MMV.Common.Polyglot import Polyglot

Speak = Polyglot.Speak

class AddNodeUI:
    def __init__(self, Editor):
        self.Editor = Editor
    
    def Here(self):
        with Dear.group() as self.AddNodesGroup: ...
    
    def Reset(self):
        Dear.delete_item(self.AddNodesGroup, children_only=True)

    def Render(self):
        with EnterDearContainerStack(self.AddNodesGroup):
            Dear.add_separator()
            Dear.add_text(Speak("Add Nodes"), color = (self.Editor.DearPyStuff.ThemeYaml.mmvSectionText))
            AN = self.Editor.Scene.AvailableNodes

            for category in sorted(AN):
                Dear.add_text(f":: {category}", color=(140,140,140))
                cat = AN[category]

                for name in cat:
                    node = cat[name]
                    Dear.add_button(
                        label=name,
                        callback=lambda d,s: self.Editor.Scene.AddNodeToScene,
                        user_data=node
                    )
