import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class StatusBar(Gtk.Statusbar):
    def __init__(self):
        super(StatusBar, self).__init__()
        self.fileCount = 0
        self.lineCount = 0
        self.matchCount = 0
        self.context_id = self.get_context_id("example")
        self.writeStatus()
        
    def writeStatus(self):
        statusBarMsg = f"Files: {self.fileCount:,}          Lines: {self.lineCount:,}              Matches: {self.matchCount:,}"
        self.remove_all(self.context_id)
        self.push(self.context_id, statusBarMsg)
        
    def updateFileCount(self, fileCount, lineCount):
        self.matchCount = 0
        self.fileCount = fileCount
        self.lineCount = lineCount
        self.writeStatus()

    def updateMatches(self, matchCount):
        self.matchCount = matchCount
        self.writeStatus()

        
