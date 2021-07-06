import copy
import logging
from abc import abstractmethod

import dearpygui.dearpygui as Dear


class TwoWayConnection:
    def __init__(self):
        self.I = None
        self.O = None


class BaseNode:
    def Init(self, InheritedNode, Editor):
        dpfx = "[BaseNode.Init]"
        self.Editor = Editor

        # Create this node's theme based on the Theme.yaml
        with Dear.theme() as self.DPG_THIS_NODE_THEME:
            if theme := self.Editor.ThemeYaml.Nodes.get(InheritedNode.Category, {}):
                logging.info(f"{dpfx} Found theme [{InheritedNode.Category}] in Theme YAML, assigning: [{theme}]")
                for key, value in theme.items():
                    self.Editor.SetDearPyGuiThemeString(key, value)
    
    # Apply theme to a DearPyGui Node
    def ApplyTheme(self):
        Dear.set_item_theme(self.DPG_NODE, self.DPG_THIS_NODE_THEME)

    @abstractmethod
    def Render(self, parent): ...

    @abstractmethod
    def Digest(self): ...

    # Node methods / Functionality
    def Delete(self):
        logging.info(f"[BaseNode] Delete Node [{self.DPG_NODE}]")
        Dear.delete_item(self.DPG_NODE)

    def Clone(self): pass

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
            Dear.add_text("Delete   ", color=text_color)

            # Clone
            Dear.add_same_line()
            Dear.add_color_button(
                label="NOT IMPLEMENTED", default_value=(0,0,255),
                callback=lambda s,d:self.Clone(),
                no_drag_drop=True, no_border=True, no_alpha=True, tracked=True
            )
            Dear.add_same_line()
            Dear.add_text("Clone   ", color=text_color)