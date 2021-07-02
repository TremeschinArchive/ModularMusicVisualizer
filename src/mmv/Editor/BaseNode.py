import copy
import logging
from abc import abstractmethod

import dearpygui.dearpygui as dear


class TwoWayConnection:
    def __init__(self):
        self.I = None
        self.O = None


class BaseNode:
    def Init(self, Editor):
        dpfx = "[BaseNode.Init]"
        self.Editor = Editor
        
        with dear.theme() as self.DPG_THEME:
            if theme := self.Editor.ThemeYaml.Nodes.get(BaseNode.category, {}):
                logging.info(f"{dpfx} Found theme [{BaseNode.category}] in Theme YAML, assigning: [{theme}]")
                for key, value in theme.items():
                    self.Editor.SetDearPyGuiThemeString(key, value)
            
    @abstractmethod
    def Render(self, parent): ... 

    @abstractmethod
    def Digest(self): ...

    # Node methods / Functionality
    def Delete(self):
        logging.info(f"[BaseNode] Delete Node [{self.DPG_NODE}]")
        dear.delete_item(self.DPG_NODE)

    def Clone(self): pass

    # Node title bar
    def AddNodeDecorator(self):
        with dear.node_attribute(attribute_type=dear.mvNode_Attr_Static):
            text_color = (255,255,255,120)

            # Delete red button
            dear.add_color_button(
                label="", default_value=(255,0,0),
                callback=lambda s,d:self.Delete(),
                no_drag_drop=True, no_border=True, no_alpha=True, tracked=True
            )
            dear.add_same_line()
            dear.add_text("Delete   ", color=text_color)

            # Clone
            dear.add_same_line()
            dear.add_color_button(
                label="NOT IMPLEMENTED", default_value=(0,0,255),
                callback=lambda s,d:self.Clone(),
                no_drag_drop=True, no_border=True, no_alpha=True, tracked=True
            )
            dear.add_same_line()
            dear.add_text("Clone   ", color=text_color)