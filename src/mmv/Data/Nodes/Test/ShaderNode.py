import dearpygui.dearpygui as Dear


def GetNode(BaseNode):
    class TestNode(BaseNode):
        def Config(self):
            self.Name = "Shader Node"
            self.Category = "Shaders"

        def Render(self, parent):
            with Dear.node(label=f"{self.Name} | ({self.Category})", parent=parent) as self.DPG_NODE:
                self.AddNodeDecorator()
                
                with Dear.node_attribute() as A:
                    Dear.add_text("Hello World" + f"  |  [{A}]" * int(self.Editor.Context.DEBUG_SHOW_IDS))

                with Dear.node_attribute(attribute_type=Dear.mvNode_Attr_Output):
                    Dear.add_slider_float(label="Output Number", width=150)
            self.ApplyTheme()
    return TestNode()
