import dearpygui.dearpygui as dear


def GetNode(BaseNode):
    class TestNode(BaseNode):
        BaseNode.name = "TestNoderrre"
        BaseNode.category = "Source"

        def Render(self, parent):
            with dear.node(label="TestNodde", parent=parent) as self.DPG_NODE:
                self.AddNodeDecorator()
                
                with dear.node_attribute() as A:
                    dear.add_text("Hello World" + f"  |  [{A}]" * int(self.Editor.Context.DEBUG_SHOW_IDS))

                with dear.node_attribute(attribute_type=dear.mvNode_Attr_Output):
                    dear.add_slider_float(label="Output Number", width=150)

            dear.set_item_theme(self.DPG_NODE, self.DPG_THEME)
    return TestNode
