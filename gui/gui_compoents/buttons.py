import wx


class BasicButton(wx.Button):
    def __init__(self, parent, id, label, pos):
        super().__init__(parent, id, label, pos)
        self.SetSize((70, 50))

    def get_chart_panel(self):
        return self.GetParent().GetParent().GetParent().chart_panel


class PipeButton(BasicButton):
    def __init__(self, parent, id, label, pos):
        super().__init__(parent, id, label, pos=pos)
        self.SetLabel("Pipe")
        self.Bind(wx.EVT_BUTTON, self.on_button_click)

    def on_button_click(self, e):
        self.draw_pipe()

    def draw_pipe(self):
        print("Drew a pipe.")
        hline = wx.StaticLine(self.get_chart_panel(),
                              -1,
                              style=wx.LI_HORIZONTAL,
                              pos=(20, 100),
                              size=wx.Size(150, 3))
        hline.SetBackgroundColour('red')


class ReactorButton(BasicButton):
    def __init__(self, parent, id, label, pos):
        super().__init__(parent, id, label, pos)
        self.SetLabel("Reactor")
        self.Bind(wx.EVT_BUTTON, self.on_button_click)

    def on_button_click(self, evt):
        print("ReactorButton on_button_click is called.")
        dc = self.get_chart_panel().dc
        print(f"dc has attr: {dir(dc)}")
        dc.SetPen(wx.Pen("red", style=wx.TRANSPARENT))
        dc.SetBrush(wx.Brush("grey", wx.SOLID))
        dc.DrawRectangle(10, 20, 30, 40)

    # def on_button_click(self, e):
    #     self.draw_reactor()
