import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk

import re

default_list = [
    ("", "", "", ""),
]

class SearchTool:
    def __init__(self, mainWindow, statusbar, configMgr ):

        self.pathFilter = ""
        self.suffixFilter = ""
        self.textFilter = ""
        
        self.mainWindow = mainWindow
        self.statusbar = statusbar
        self.configMgr = configMgr
        
        self.page = Gtk.Box()
        self.page.set_border_width(10)

        # Setting up the grid in which the elements are to be positioned
        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        self.page.add(grid)

        # Creating the ListStore
        self.liststore = Gtk.ListStore(str, str, str, str)
        for list_ref in default_list:
            self.liststore.append(list(list_ref))

        # creating the treeview, and adding the columns
        treeview = Gtk.TreeView(model=self.liststore)
        treeview.set_grid_lines(Gtk.TreeViewGridLines.BOTH)
        for i, column_title in enumerate(
            ["FileName", "Type", "Line", "Text"]
        ):
            renderer = Gtk.CellRendererText(editable=True)
            renderer.colIdx = i
            renderer.connect('edited', self.cell_edited)
            
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)

            # Allow user to resize the columns
            column.set_resizable(True)

            # Do not autosize when model data changes
            column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            
            if i==0:
                column.set_fixed_width(400)
            if i==2:
                column.set_fixed_width(70)

            treeview.append_column(column)


        # Set up drag and drop source
        treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                          [],
                                          Gdk.DragAction.COPY)

        treeview.drag_source_add_uri_targets()
        treeview.connect("drag-data-get", self.drag_data_get)

                
        # setting up the layout, putting the treeview in a scrollwindow
        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.set_hexpand(True)

        grid.attach(self.scrollable_treelist, 0, 0,3, 20)

        self.scrollable_treelist.add(treeview)

        self.page.show_all()


    def cell_edited(self, widget, rowNumber, text):
        if rowNumber == "0":
            if widget.colIdx==0: 
                self.pathFilter = text
            elif widget.colIdx==1:
                self.suffixFilter = text
            elif widget.colIdx==3:
                self.textFilter = text
            self.updateSearchResults()

    def drag_data_get (self, treeview, drag_context, data, info, time):
        model, path = treeview.get_selection().get_selected_rows()

        # There may be many selected rows; get the first
        selectedRow = path[0] 

        # Get the data at selectedRow, column 0 and 1
        selectedFilePath = model[selectedRow][0]
        selectedSuffix = model[selectedRow][1]
        if (selectedSuffix):
            selectedFilePath = selectedFilePath + "." + selectedSuffix

        fileUri = "file://" + selectedFilePath
            
        uriList = [fileUri]
        data.set_uris(uriList)
            
    def updateSearchResults(self):
        self.liststore.clear()
        searchFilter = [self.pathFilter, self.suffixFilter, "", self.textFilter]
        self.liststore.append( searchFilter )

        nMatches = 0

        if self.pathFilter == ""    \
        and self.suffixFilter == "" \
        and self.textFilter == "":  \
            return

        if len(self.configMgr.allFilesLines) == 0:
            return

        caseSens = self.configMgr.caseSensitive.get_active()
        useRegEx = self.configMgr.regularExpression.get_active()

        self.continueSearch = True
        
        if self.textFilter == "":
            # Simple filename and file type search
            
            for filePath in self.configMgr.allFilesLines.keys():
                if not self.continueSearch:
                    break
                
                parts = filePath.rsplit('.',1) # Split on 1st occurance from the end
                filePrefix = filePath
                fileSuffix = ""
                if len(parts) >1:
                    fileSuffix = parts[-1] # final element 
                    filePrefix = parts[-2] # the remainder

                    if self.fancyCompare(self.pathFilter,
                                         filePrefix,
                                         caseSens,
                                         useRegEx)    \
                    and self.fancyCompare(self.suffixFilter,
                                          fileSuffix,
                                          caseSens,
                                          useRegEx):
                
                        lines = self.configMgr.allFilesLines[filePath]
                        firstLine = lines[0].strip()
                        resultRow = [filePrefix, fileSuffix, "1", firstLine]
                        self.liststore.append(resultRow)

                        nMatches += 1
                        if nMatches >= self.configMgr.maxMatchesInt:
                            break

        else:
            # Full text search
            for filePath in self.configMgr.allFilesLines.keys():
                if nMatches >= self.configMgr.maxMatchesInt:
                    break
                parts = filePath.rsplit('.',1) # Split on 1st occurance from the end
                filePrefix = filePath
                fileSuffix = ""
                if len(parts) >1:
                    fileSuffix = parts[-1] # final element 
                    filePrefix = parts[-2] # the remainder
            
                    if self.fancyCompare(self.pathFilter,
                                         filePrefix,
                                         caseSens,
                                         useRegEx)    \
                    and self.fancyCompare(self.suffixFilter,
                                          fileSuffix,
                                          caseSens,
                                          useRegEx):
                
                        # The file name and suffix match. So now
                        # check if there are any matching text lines within
                        # the file
                        lines = self.configMgr.allFilesLines[filePath]
                        lineNum = 0
                        for line in lines:
                            lineNum+=1
                            strippedLine = line.strip()
                            if self.fancyCompare(self.textFilter,
                                                 strippedLine,
                                                 caseSens,
                                                 useRegEx):
                                resultRow = [filePrefix,
                                             fileSuffix,
                                             str(lineNum),
                                             strippedLine]
                                self.liststore.append(resultRow)

                                nMatches += 1
                                if nMatches >= self.configMgr.maxMatchesInt:
                                    break

        self.statusbar.updateMatches(nMatches)

        
    def fancyCompare(self, pattern, text, caseSens, useRegEx ):
        if not self.continueSearch:
            return False
        
        if not pattern:
            return True

        # Regular Expression search
        if useRegEx:
            try:
                if re.search( pattern, text):
                    return True
                else:
                    return False
            except:
                self.continueSearch = False

                dialog = Gtk.MessageDialog(
                    transient_for=self.mainWindow,
                    flags=0,
                    message_type=Gtk.MessageType.ERROR,
                    buttons=Gtk.ButtonsType.OK,
                    text="Bad Regular Expression",
                )
                dialog.run()
                dialog.destroy()
                return False

        # Case Sensitive search
        if caseSens:
            if pattern in text:
                return True
            else:
                return False
        else:         # Case Insensitive search
            if pattern.lower() in text.lower():
                return True
            else:
                return False;


