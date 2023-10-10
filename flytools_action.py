import os

import pcbnew
import wx

from . import flytools

class FlyToolsAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "flytime"
        self.category = ""
        self.description = "Calculates net delay in the time domain"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flytools_32x32.png')

    def error(self, msg):
        wx.MessageBox(msg, "Error", wx.OK | wx.ICON_ERROR)

    def Run(self):
        pcbnew_window = wx.FindWindowByName("PcbFrame")
        board = pcbnew.GetBoard()
        if pcbnew_window is None:
            # Something failed, abort
            self.error("Failed to find pcbnew main window")
            return
        try:
            flytools_frame = flytools.FlyToolsFrame(board, parent=pcbnew_window,
                                                    style=wx.FRAME_FLOAT_ON_PARENT | wx.DEFAULT_FRAME_STYLE)
        except Exception as e:
            self.error("Failed to create flytools frame: {}".format(e))
            return
        flytools_frame.Show()

