import wx

from gui.gui_compoents.frame import MainFrame


class MainApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None, -1, 'Poopy Lab')
        frame.Show()
        return True