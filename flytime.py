#!/usr/bin/env python3

import os
import random

from fltk import *
import pcbnew

import flytools

class FlyWindow(Fl_Double_Window):
    def __init__(self, w, h, label, ftools: flytools.FlyTools, flysheet: flytools.FlySheet):
        super().__init__(w, h, label)

        icon = Fl_PNG_Image(os.path.join(os.path.dirname(__file__), "flytime.png"))
        self.icon(icon)

        self.flytools = ftools
        self.flysheet = flysheet

        self.begin()
        self.sheetnamein = Fl_Input(120, 10, 200, 25, "Sheet Name")
        self.refnetin = Fl_Input(120, 40, 200, 25, "Reference Net: ")
        self.targetnetin = Fl_Input(120, 70, 200, 25, "Target Net: ")
        self.setnetsbtn = Fl_Button(10, 105, w-20, 30, "Set Nets")

        self.refdelayout = Fl_Output(140, 145, 180, 25, "Reference Delay: ")
        self.targetdelayout = Fl_Output(140, 175, 180, 25, "Target Delay: ")
        self.diffout = Fl_Output(140, 205, 180, 25, "Difference: ")

        self.updatebtn = Fl_Button(10, 240, w-20, 30, "Update Spreadsheet")
        self.end()

        self.refnet = None
        self.targetnet = None

        self.callback(self.win_cb)
        self.setnetsbtn.callback(self.setnets)
        self.updatebtn.callback(self.update_spreadsheet)

        Fl_add_timeout(0.3, self.check_pcb)

    def win_cb(self, wid):
        if Fl.event() == FL_SHORTCUT and Fl.event_key() == FL_Escape:
            return
        sys.exit(0)

    def update_delays(self):
        if self.refnet is None or self.targetnet is None:
            return
        refdelay = self.flytools.get_net_delay(self.refnet)
        refnetrow = self.flysheet.getRowByName(self.refnet.GetShortNetname())
        refdelay += self.flysheet.getFloatValue(refnetrow, "Extra Delay")
        refdelay += self.flysheet.getFloatValue(refnetrow, "Package Delay")

        targetdelay = self.flytools.get_net_delay(self.targetnet)
        targetnetrow = self.flysheet.getRowByName(self.targetnet.GetShortNetname())
        targetdelay += self.flysheet.getFloatValue(targetnetrow, "Extra Delay")
        targetdelay += self.flysheet.getFloatValue(targetnetrow, "Package Delay")

        self.refdelayout.value(str(round(refdelay, 2)))
        self.targetdelayout.value(str(round(targetdelay, 2)))
        self.diffout.value(str(round(targetdelay-refdelay, 2)))

    def check_pcb(self):
        if self.flytools.is_pcb_modified():
            print("PCB was modified, reloading board and updating nets")
            self.flytools.reload()
            self.update_delays()
        Fl_add_timeout(0.3, self.check_pcb)

    def update_spreadsheet(self, wid):
        self.flysheet.reload()
        print("Updating spreadsheet")
        try:
            self.flysheet.updateAll()
        except Exception as e:
            fl_alert(str(e))

    def setnets(self, wid):
        print("Updating nets")
        sheetname = self.sheetnamein.value()
        self.flysheet.setSheet(sheetname)
        try:
            self.refnet = self.flytools.shortname_to_net(self.refnetin.value())
            self.targetnet = self.flytools.shortname_to_net(self.targetnetin.value())
            self.update_delays()
        except Exception as e:
            fl_alert(str(e))
            return

if __name__ == "__main__":
    pcbname = fl_file_chooser("Select PCB file", "*.kicad_pcb", None, 0)
    if pcbname is None:
        sys.exit(1)
    prjpath = os.path.dirname(pcbname)
    flytime_infofile = os.path.join(prjpath, "flytime_info.json")
    if not os.path.exists(flytime_infofile):
        flytime_infofile = fl_file_chooser("Select Flytime info file", "*.json", None, 0)
        if flytime_infofile is None:
            sys.exit(1)
    sheetname = fl_file_chooser("Select Spreadsheet file", "*.xlsx", None, 0)
    if sheetname is None:
        sys.exit(1)
    print("Loading PCB")
    board = pcbnew.LoadBoard(pcbname)
    ftools = flytools.FlyTools(board, flytime_infofile)
    flysheet = flytools.FlySheet(sheetname, ftools)
    win = FlyWindow(330, 280, "FlyTime", ftools, flysheet)
    win.show()
    Fl.run()
