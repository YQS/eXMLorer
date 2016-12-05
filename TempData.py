#encoding: UTF-8

import ConfigParser
from os.path import isfile

import globals as GL 

'''
datos temporales no configurables:
GLOBALES:
lastVisitedFolder
treeviewColumnsSize

PER FILE:
lastSelectedTag
'''

class TempData(ConfigParser.RawConfigParser):
    def __init__(self, filename):
        ConfigParser.RawConfigParser.__init__(self)
        self.filename = filename
        for section in GL.tempDataSections:
            self.add_section(section)
        #self.add_section('GLOBAL')
        #self.add_section('FILE')
        self.loadData()
        
    def __del__(self):
        with open(self.filename, 'wb') as file:
            self.write(self.filename)
        
    def loadData(self):
        if isfile(self.filename):
            self.read(self.filename)
        else:
            self.createFile()
            
    def createFile(self):
        self.set('GLOBAL', 'lastVisitedFolder', '')
        self.set('GLOBAL', 'treeviewColumnSize_subname', 120)
        self.set('GLOBAL', 'treeviewColumnSize_data', 480)
        self.set('FILE', 'lastFocusTag', None)
        with open(self.filename, 'wb') as file:
            self.write(file)
            
    def getValue(self, key):
        value = None
        for section in GL.tempDataSections:
            try:
                value = self.get(section, key)
                if value <> None:
                    break
            except:
                pass
        return value
    
    def setValue(self, key, value):
        for section in GL.tempDataSections:
            try:
                self.set(section, key, value)
            except:
                pass