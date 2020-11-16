#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  config.py
#
#  Copyright 2020 John Coppens <john@jcoppens.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import simplejson as json

DEFAULT_CONF_FILE = "~/.rt.ini"

DEFAULT_CONFIG = """
{
"image": {
    "width": 400,
    "height": 300},
"editor": {
    "linenrs": 1},
"scene": {
    "ambient": 0.1}
}
"""


class Config(Gtk.Frame):
    def __init__(self):
        super(Config, self).__init__(
            label = "Configuration",
            margin = 6)

        self.conf = json.loads(DEFAULT_CONFIG)
        self.grid = Gtk.Grid(
                    margin = 6,
                    row_spacing = 4,
                    column_spacing = 10)

        y = 0
        for spec in (
                    ("Image:",          "image"),
                    ( "Width:",         int,    "width",
                                        Gtk.Entry,  6),
                    ( "Height:",        int,    "height",
                                        Gtk.Entry,  6),

                    ("Editor:",         "editor"),
                    ( "Line numbers:",  bool,   "linenrs",
                                        Gtk.CheckButton),
                    ("Scene:",          "scene"),
                    (  "Ambient light:", int,   "ambient",
                                        Gtk.Entry,  12)):
            if len(spec) == 2:
                lbl = Gtk.Label(label = spec[0])
                self.grid.attach(lbl, 0, y, 1, 1)
                self.section = spec[1]
                y += 1

            else:
                cap, typ, field = spec[:3]
                rest = spec[3:]

                lbl = Gtk.Label(label = cap, xalign = 1)
                self.grid.attach(lbl, 1, y, 1, 1)

                if rest[0] == Gtk.Entry:
                    wdg, width = rest
                    w = wdg(width_chars = width,
                        text = "{}".format(self.get_field(self.section, field)))
                    w.connect("changed", self.on_widget_change, self.section, field)

                elif rest[0] == Gtk.CheckButton:
                    wdg, = rest
                    w = wdg(active = field)
                    w.connect("toggled", self.on_widget_change, self.section, field)

                self.grid.attach(w, 2, y, 1, 1)
                y += 1

        self.add(self.grid)
        print("Configuration: ", self.conf)


    def on_widget_change(self, wdg, section, field):
        if isinstance(wdg, Gtk.Entry):
            try:
                self.set_field(section, field, int(wdg.get_text(), 0))
            except:
                self.set_field(section, field, 0)

        elif isinstance(wdg, Gtk.CheckButton):
            self.set_field(section, field, 1 if wdg.get_active() else 0)


    def set_field(self, section, param, value):
        self.conf[section][param] = value


    def get_field(self, section, param):
        return self.conf[self.section][param]


    def save(self):
        pass


    def load(self):
        pass



class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", lambda x: Gtk.main_quit())
        self.set_default_size(400, 300)

        config = Config()

        self.add(config)
        self.show_all()

    def run(self):
        Gtk.main()


def main(args):
    mainwdw = MainWindow()
    mainwdw.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
