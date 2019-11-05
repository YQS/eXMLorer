# encoding: UTF-8

import ConfigParser
from os.path import isfile

from config import Globals as GL

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
        for section in GL.temp_data_sections:
            self.add_section(section)
        self.load_data()

    def __del__(self):
        with open(self.filename, 'wb') as file:
            self.write(self.filename)

    def load_data(self):
        if isfile(self.filename):
            self.read(self.filename)
        else:
            self.create_file()

    def create_file(self):
        self.set('GLOBAL', 'lastVisitedFolder', '')
        self.set('GLOBAL', 'treeviewColumnSize_subname', 120)
        self.set('GLOBAL', 'treeviewColumnSize_data', 480)
        self.set('FILE', 'lastFocusTag', None)
        with open(self.filename, 'wb') as temp_file:
            self.write(temp_file)

    def get_value(self, key):
        value = None
        for section in GL.temp_data_sections:
            try:
                value = self.get(section, key)
                if value is not None:
                    break
            except:
                pass
        return value

    def set_value(self, key, value):
        for section in GL.temp_data_sections:
            try:
                self.set(section, key, value)
            except:
                pass
