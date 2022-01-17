import wx
import os
from gui.gui_compoents.panels import ButtonPanel, ChartPanel


class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 500))
        print(os.getcwd())
        icon = wx.IconLocation('data/icon.png')
        self.SetIcon(wx.Icon(icon))
        # top panel
        top_panel = wx.Panel(self)

        screen_width, screen_height = wx.GetDisplaySize()
        BUTTON_PANEL_HEIGHT = 100

        self.button_panel = ButtonPanel(top_panel, 1, pos=(0, 0), size=(screen_width, BUTTON_PANEL_HEIGHT))

        self.chart_panel = ChartPanel(top_panel, 2, pos=(0, 100), size=(screen_width, screen_height - BUTTON_PANEL_HEIGHT))

        # sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.button_panel, 0, wx.ALIGN_CENTER_HORIZONTAL, border=10)
        sizer.Add(self.chart_panel, 0, wx.ALIGN_CENTER_HORIZONTAL, border=10)
        top_panel.SetSizer(sizer)

        # full screen
        self.Maximize()