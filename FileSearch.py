
# FileSearch.py, based on the C# app of the same name
# Uses the GTK notebook class for tab view
# 2020-12-27

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from SearchTool import SearchTool
from ConfigMgr import ConfigMgr
from StatusBar import StatusBar

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Filesearch v0.1")
        self.set_default_size(1400,800)
        self.set_border_width(3)

        mainview = Gtk.VBox()
        self.add(mainview)

        # Create a tabbed view
        tabbedview = Gtk.Notebook()
        tabbedview.set_vexpand(True)
        mainview.pack_start(tabbedview, True, True, 0)

        self.statusbar = StatusBar()
        self.configMgr = ConfigMgr( self.statusbar )

        self.set_icon_from_file(self.configMgr.get_resource_path("Search.png"))

        mainWindow = self
        self.searchTool = SearchTool( mainWindow, self.statusbar, self.configMgr )

        tabbedview.append_page(self.searchTool.page, Gtk.Label(label="Search"))        
        tabbedview.append_page(self.configMgr.page, Gtk.Label(label="Config"))

        mainview.pack_end( self.statusbar, False, False, 0)

        
win = MyWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
