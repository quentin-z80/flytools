import os

import pcbnew
import wx

from . import flytools

class FlySelectedAction(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Flytime of selected elements"
        self.category = "Flytime of selected elements"
        self.description = "Calculates the total delay of all selected elements"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'flytime_32x32.png') # Optional

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

        self.ftools = flytools.FlyTools(self.board, flytime_infofile, standalone=False)
        self.showDelay()

    def showDelay(self):
        delay = 0
        tracks = 0
        vias = 0
        for item in self.ftools.selected_items():
            if item.GetClass() == "PCB_TRACK" or item.GetClass() == "PCB_ARC":
                tracks += 1
            elif item.GetClass() == "PCB_VIA":
                vias += 1
            delay += self.ftools.get_element_delay(item)

        delay = round(delay, 2)
        wx.MessageDialog(self.pcbnew_frame, f"Tracks: {tracks}, Vias: {vias}\nTotal delay: {delay} ps", "Flytime of selected elements", wx.OK).ShowModal()
