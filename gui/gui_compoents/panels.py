import wx
from gui.gui_compoents.buttons import ReactorButton, PipeButton


class ButtonPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(ButtonPanel, self).__init__(parent, id, pos, size)
        button1 = ReactorButton(self, 1, label='', pos=(20, 10))
        button3 = PipeButton(self, 3, label='', pos=(100, 10))


class ChartPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
        super(ChartPanel, self).__init__(parent, id, pos, size)
        self.SetBackgroundColour('gray')
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, evt):
        print("ChartPanel OnPaint is called.")
        self.dc = wx.PaintDC(self)
