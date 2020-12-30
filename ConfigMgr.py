import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from pathlib import Path

import json

class ConfigMgr:
    def __init__(self, statusbar ):
        self.statusbar = statusbar

        self.paramFile = "/home/ianc/python/gtk/FileSearch.json"
        self.paramDict = {}

        try:
            param_file = open(self.paramFile, "r")
            lines = param_file.readlines()
            json_string = lines[0]
            param_file.close()
            self.paramDict = json.loads(json_string)
        except:
            pass
        
        
        # Page layout
        self.page = Gtk.Box()
        self.page.set_border_width(10)
        
        grid = Gtk.Grid()
        grid.set_row_spacing(6);

        workspaceLabel = Gtk.Label(label="Workspace: ")
        grid.add(workspaceLabel)
        self.workspace = Gtk.Entry()
        if "Workspace" in self.paramDict:
            self.workspace.set_text( self.paramDict["Workspace"])
                                      
        self.workspace.set_width_chars(80)
        grid.attach_next_to( self.workspace,
                             workspaceLabel,
                             Gtk.PositionType.RIGHT, 1, 1)

        filePatternLabel = Gtk.Label(label="File Pattern: ")        
        self.filePattern = Gtk.Entry()
        if "FilePattern" in self.paramDict:
            self.filePattern.set_text( self.paramDict["FilePattern"])

        grid.attach_next_to( filePatternLabel,
                             workspaceLabel,
                             Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to( self.filePattern,
                             filePatternLabel,
                             Gtk.PositionType.RIGHT, 1, 1)

        spacer = Gtk.Label(label="")
        grid.attach_next_to( spacer,
                             filePatternLabel,
                             Gtk.PositionType.BOTTOM, 1, 1)
        
        loadButton = Gtk.Button(label="Load")
        loadButton.connect("clicked", self.on_load_button_clicked)
        grid.attach_next_to( loadButton,
                             spacer,
                             Gtk.PositionType.BOTTOM, 1, 1)
        
        # Separate the search configuration
        spacer = Gtk.Label(label="")
        grid.attach_next_to( spacer,
                             loadButton,
                             Gtk.PositionType.BOTTOM, 1, 1)

        spacer2 = Gtk.Label(label="")
        grid.attach_next_to( spacer2,
                             spacer,
                             Gtk.PositionType.BOTTOM, 1, 1)
        
        caseSensitiveLabel = Gtk.Label(label="   Case Sens:")
        self.caseSensitive = Gtk.CheckButton()
        self.caseSensitive.set_label("")

        grid.attach_next_to( caseSensitiveLabel,
                             spacer2,
                             Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to( self.caseSensitive,
                             caseSensitiveLabel,
                             Gtk.PositionType.RIGHT, 1, 1)

        regularExpressionLabel = Gtk.Label(label="Regular Exp:")
        self.regularExpression = Gtk.CheckButton()
        self.regularExpression.set_label("")
        
        grid.attach_next_to( regularExpressionLabel,
                             caseSensitiveLabel,
                             Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to( self.regularExpression,
                             regularExpressionLabel,
                             Gtk.PositionType.RIGHT, 1, 1)
        
        maxMatchesLabel =  Gtk.Label(label="Max Results: ")
        self.maxMatches = Gtk.Entry()
        if "MaxMatches" in self.paramDict:
            self.maxMatches.set_text( self.paramDict["MaxMatches"])
                                       
        grid.attach_next_to( maxMatchesLabel,
                             regularExpressionLabel,
                             Gtk.PositionType.BOTTOM, 1, 1)
        grid.attach_next_to( self.maxMatches,
                             maxMatchesLabel,
                             Gtk.PositionType.RIGHT, 1, 1)

        self.page.add(grid)

        # A dictionary where the key is the path + filename,
        # and the value is a string list containing the lines of text in the file
        self.allFilesLines = {}

        
    def on_load_button_clicked(self, widget):

        workspace = self.workspace.get_text()
        filePattern = self.filePattern.get_text()
        maxMatches = self.maxMatches.get_text()
        self.maxMatchesInt = int(maxMatches)
        self.paramDict["Workspace"] = workspace
        self.paramDict["FilePattern"] = filePattern
        self.paramDict["MaxMatches"] = maxMatches
        json_string = json.dumps(self.paramDict)
        param_file = open(self.paramFile, "w")
        param_file.write(json_string)
        param_file.close()

        self.allFilesLines = {}
        fileCount = 0
        lineCount = 0
        
        patterns = filePattern.split(';')
        for pattern in patterns:
            for path in Path(workspace).rglob(pattern):
                filename = str(path.absolute())
                text_file = open(filename, "r", errors='ignore')
                lines = text_file.readlines()

                nLines = len(lines)
                self.allFilesLines[filename] = lines

                fileCount += 1
                lineCount += nLines
                self.statusbar.updateFileCount(fileCount, lineCount)
                

