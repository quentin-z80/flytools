import os

import pcbnew
import wx

from . import flytools

DEBUG = True

if DEBUG:
    import debugpy
    debugpy.listen(5678)
    debugpy.wait_for_client()

class FlyTime(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "flytime"
        self.category = ""
        self.description = "Calculates net delay in the time domain"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flytime_32x32.png')

    def Run(self):

        self.board = pcbnew.GetBoard()
        prjpath = os.path.dirname(self.board.GetFileName())
        self.pcbnew_frame = wx.GetTopLevelParent(wx.GetActiveWindow())

        flytime_infofile = os.path.join(prjpath, "flytime_info.json")
        if not os.path.exists(flytime_infofile):
            with wx.FileDialog(self.pcbnew_frame, "Open Flytime info file", wildcard="JSON files (*.json)|*.json",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return

                flytime_infofile = fileDialog.GetPath()
