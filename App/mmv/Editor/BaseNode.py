"""
===============================================================================
                                GPL v3 License                                
===============================================================================

Copyright (c) 2020 - 2021,
  - Tremeschin < https://tremeschin.gitlab.io > 

===============================================================================

Purpose: Define the base functionality of a Node

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
import copy
import logging
from abc import abstractmethod

import dearpygui.dearpygui as Dear

from mmv.Editor.Localization import Polyglot

Speak = Polyglot.Speak

class BaseNode:
    def Init(self, InheritedNode, Editor):
        dpfx = "[BaseNode.Init]"
        self.Editor = Editor
        self.Config()

        # Create this node's theme based on the Theme.yaml
        with Dear.theme() as self.DPG_THIS_NODE_THEME:
            if theme := self.Editor.ThemeYaml.Nodes.get(InheritedNode.Category, {}):
                logging.info(f"{dpfx} Found theme [{InheritedNode.Category}] in Theme YAML, assigning: [{theme}]")
                for key, value in theme.items():
                    self.Editor.SetDearPyGuiThemeString(key, value)

    # Node title bar
    def AddNodeDecorator(self):
        with Dear.node_attribute(attribute_type=Dear.mvNode_Attr_Static):
            text_color = (255,255,255,120)

            # Delete red button
            Dear.add_color_button(
                label="", default_value=(255,0,0),
                callback=lambda s,d:self.Delete(),
                no_drag_drop=True, no_border=True, no_alpha=True, tracked=True
            )
            Dear.add_same_line()
            Dear.add_text(Speak("Delete") + "   ", color=text_color)

            # Clone
            Dear.add_same_line()
            Dear.add_color_button(
                label="NOT IMPLEMENTED", default_value=(0,0,255),
                callback=lambda s,d:self.Clone(),
                no_drag_drop=True, no_border=True, no_alpha=True, tracked=True
            )
            Dear.add_same_line()
            Dear.add_text(Speak("Clone") + "   ", color=text_color)

    # Apply theme to a DearPyGui Node
    def ApplyTheme(self):
        Dear.set_item_theme(self.DPG_NODE_ID, self.DPG_THIS_NODE_THEME)

    @abstractmethod
    def Render(self, parent): ...

    @abstractmethod
    def Digest(self): ...

    # Node methods / Functionality
    def Delete(self):
        logging.info(f"[BaseNode] Delete Node [{self.DPG_NODE_ID}]")
        Dear.delete_item(self.DPG_NODE_ID)

    def Clone(self): pass
