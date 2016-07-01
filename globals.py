# encoding: UTF-8

import dicext as DICEXT
import app_language as LANG

# GLOBAL VARIABLES

filename = ''
lastFolderVisited = ''
XMLTree = None
XMLEncoding = ''
#XMLParentMap = {}
dicTagsInTree = {}
appTreeView = None
lastTreeViewFocus = None
defaultPrettyPrint = True
eliminateSpaceInSelfClosingTag = True

names = LANG.spanish

buttonWidth = 15
labelButtonWidth = 50
labelExtraButtonWidth = 8

marginToExtendToText = 30
dataColumnTextLimit = 100

dicTagSubnames = DICEXT.DictionaryFile('namedic')
