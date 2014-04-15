
class GuiTool(object):

    def __init__(self, controller):
        self.controller = controller

    def OnKeyPress(self, keycode, event):
        raise AttributeError()

    def OnMouseDown(self, x, y, lastx, lasty, event):
        raise AttributeError()

    def OnMouseUp(self, event):
        raise AttributeError()

    def OnMouseMotion(self, x, y, lastx, lasty, event):
        raise AttributeError()

