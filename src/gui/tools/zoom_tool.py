
from gui_tool import GuiTool

class ZoomTool(GuiTool):

    def __init__(self, name):
        super(ZoomTool, self).__init__(name)

    def OnMouseMotion(self, x, y, lastx, lasty, event):

        if event.Dragging() and event.LeftIsDown():
            self.controller.viewport.scale = self.controller.viewport.scale * 1.01 ** (y - lasty)
            self.controller.updateView()
            return True
        return False

