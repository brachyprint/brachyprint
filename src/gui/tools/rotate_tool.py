
from gui_tool import GuiTool

class RotateTool(GuiTool):

    def __init__(self, controller):
        super(RotateTool, self).__init__(controller)

    def OnMouseMotion(self, x, y, lastx, lasty, event):

        if event.Dragging() and event.LeftIsDown():
            self.controller.viewport.theta += 0.1 * (y - lasty)
            self.controller.viewport.phi += - 0.1 * (x - lastx)

