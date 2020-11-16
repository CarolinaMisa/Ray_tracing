#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  rt.py
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
gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')
gi.require_version('Pango', '1.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gdk, Gtk, GooCanvas, Pango, GtkSource

from PIL import Image
from parse import Pov_parser
import json
from config import Config
from scene import Scene

PROG = "RT"
VERSION = "0.10.19"
MAIN_TITLE = "UCC rt.py v" + VERSION


rt_css = b"""
#code {
    font-family: Monospace;
    font-size: 10pt;
}
"""

def set_styles():
    """ Proveedor de css para el programa
    """
    provider = Gtk.CssProvider()
    provider.load_from_data(rt_css)
    Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


class MainMenu(Gtk.MenuBar):
    def __init__(self, toplevel):
        super(MainMenu, self).__init__()
        self.main_menu = {}
        self.toplevel = toplevel

        for key in ["File", "Edit", "Tools", "Help"]:
            item = Gtk.MenuItem(label = key)
            self.main_menu[key] = Gtk.Menu()
            item.set_submenu(self.main_menu[key])
            self.add(item)

        self.add_items_to("File", (("Quit", lambda x: Gtk.main_quit()), ))
        self.add_items_to("Help", (("About", self.on_about_activated), ))


    def add_items_to(self, main_item, items):
        for item, handler in items:
            if item == None:
                it = Gtk.SeparatorMenuItem()
            else:
                it = Gtk.ImageMenuItem(label = item)
                it.connect("activate", handler)
            self.main_menu[main_item].insert(it, 0)


    def on_about_activated(self, menuitem):
        dlg = Gtk.AboutDialog(version = VERSION,
                              program_name = PROG,
                              license_type = Gtk.License.GPL_3_0)
        dlg.set_transient_for(self.toplevel)
        dlg.run()
        dlg.destroy()



class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.connect("destroy", lambda x: Gtk.main_quit())
        self.set_title(MAIN_TITLE)
        self.set_default_size(800, 500)
        set_styles()

        vbox = Gtk.VBox()

        # Agregar el menu principal
        mainmenu = MainMenu(self)
        mainmenu.add_items_to("File", (
                ("Save scene file como ...", self.on_save_scene_as),
                ("Open scene file...", self.on_open_scene)))
        mainmenu.add_items_to("Tools", (("Renderizar", self.on_render_clicked), ))
        vbox.pack_start(mainmenu, False, False, 0)

        # Agregar notebook con editor y imagen
        self.nb = Gtk.Notebook()
        vbox.pack_start(self.nb, True, True, 0)

        # Creamos al editor y lo agregamos a la notebook
        self.edit_buffer = GtkSource.Buffer()
        editor = GtkSource.View(
                    name = "code",
                    buffer = self.edit_buffer)
        edit_scroller = Gtk.ScrolledWindow()
        edit_scroller.add(editor)
        self.nb.append_page(edit_scroller, Gtk.Label(label = "Editor"))

        # Creamos la pestaña para la imagen
        img_scroller = Gtk.ScrolledWindow()
        self.render = Gtk.Image()
        img_scroller.add(self.render)
        self.nb.append_page(img_scroller, Gtk.Label(label = "Render"))

        # Creamos la pestaña para la configuracion
        self.config = Config()
        self.nb.append_page(self.config, Gtk.Label(label = "Configure"))

        self.add(vbox)
        self.show_all()


    def on_open_scene(self, menuitem):
        """ Abrir un archivo (*.rt) con una escena (compatible con
            POV-ray
        """
        fc = Gtk.FileChooserDialog(
                    parent = self,
                    action = Gtk.FileChooserAction.OPEN)

        for glob, title in (("*.rt", "Ray tracer files (*.rt)"),
                            ("*", "All files (*)")):
            filt = Gtk.FileFilter()
            filt.add_pattern(glob)
            filt.set_name(title)
            fc.add_filter(filt)

        fc.add_buttons(
                    "Cancel", Gtk.ResponseType.CANCEL,
                    "Ok", Gtk.ResponseType.OK)

        if fc.run() == Gtk.ResponseType.OK:
            fname = fc.get_filename()
            with open(fname) as infile:
                text = infile.read()
            self.edit_buffer.set_text(text)

        fc.destroy()


    def on_save_scene_as(self, menuitem):
        """ Guardar el texto en el editor a disco, a un archivo *.rt
        """
        fc = Gtk.FileChooserDialog(
                    parent = self,
                    do_overwrite_confirmation = True,
                    action = Gtk.FileChooserAction.SAVE)

        for glob, title in (("*.rt", "Ray tracer files (*.rt)"),
                            ("*", "All files (*)")):
            filt = Gtk.FileFilter()
            filt.add_pattern(glob)
            filt.set_name(title)
            fc.add_filter(filt)

        fc.add_buttons(
                    "Cancel", Gtk.ResponseType.CANCEL,
                    "Save", Gtk.ResponseType.OK)

        if fc.run() == Gtk.ResponseType.OK:
            fname = fc.get_filename()
            with open(fname, "w") as outfile:
                text = self.edit_buffer.get_text(
                            self.edit_buffer.get_start_iter(),
                            self.edit_buffer.get_end_iter(),
                            False)
                outfile.write(text)


        fc.destroy()


    def on_render_clicked(self, menuitem):
        """ Entrada = Contenido del editor -> parser
            Parsear -> ParseResult
            ParseResult -> Classifier -> Scene
            Scene -> Tracer
        """
        eb = self.edit_buffer
        text = eb.get_text(eb.get_start_iter(), eb.get_end_iter(), False)
        if len(text) == 0:
            dialog = Gtk.MessageDialog(
                        parent = self,
                        message_type = Gtk.MessageType.ERROR,
                        text = "¡No hay script para renderizer!")
            dialog.add_buttons("Ok", Gtk.ResponseType.ACCEPT)
            dialog.run()
            dialog.destroy()
            return

        self.nb.set_current_page(1)

        pparser = Pov_parser()
        parser = pparser.make_parser()
        result = parser.parseString(text)

        scene = Scene()
        scene.classify(result)
        scene.tracer(self)


    def run(self):
        Gtk.main()


def main(args):
    mainwdw = MainWindow()
    mainwdw.run()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
