# encoding: UTF-8

import dicext as DICEXT

# GLOBAL VARIABLES

filename = ''
lastFolderVisited = ''
XMLTree = None
XMLParentMap = {}
dicTagsInTree = {}
appTreeView = None
lastTreeViewFocus = None

buttonWidth = 15
labelButtonWidth = 50
labelExtraButtonWidth = 8

marginToExtendToText = 30
dataColumnTextLimit = 100

dicTagSubnames = DICEXT.DictionaryFile('namedic')
