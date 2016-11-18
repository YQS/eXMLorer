# encoding: UTF-8

import dicext as DICEXT
import app_language as LANG

import ConfigParser
from os.path import isfile

# GLOBAL VARIABLES

filename = ''
lastFolderVisited = ''
XMLTree = None
XMLEncoding = ''
#XMLParentMap = {}
dicTagsInTree = {}
appTreeView = None
lastTreeViewFocus = None

#MODULES GLOBALS
moduleDirectory = 'modules'
moduleDic = {}

#CONFIGURABLES FROM CFG
configFileName = 'config.cfg'
defaultPrettyPrint = True
eliminateSpaceInSelfClosingTag = True
linefyAtSave = True
caseSensitiveSearch = False
useSQLButtons = False
showComments = True
names = LANG.spanish

#SIZES
buttonWidth = 15
labelButtonWidth = 50
labelExtraButtonWidth = 8

marginToExtendToText = 30
dataColumnTextLimit = 100

dicTagSubnames = DICEXT.DictionaryFile('namedic')

def globalVarsStart():
	global configFileName
	global defaultPrettyPrint, eliminateSpaceInSelfClosingTag, caseSensitiveSearch, useSQLButtons, showComments, names
	if not isfile(configFileName):
		createConfigFile(configFileName)
		
	config = ConfigParser.RawConfigParser()
	config.read(configFileName)
	
	defaultPrettyPrint = config.getboolean('Configuration', 'pretty_print')
	eliminateSpaceInSelfClosingTag = config.getboolean('Configuration', 'no_spaces_in_closed_tag')
	linefyAtSave = config.getboolean('Configuration', 'linefy_at_save')
	caseSensitiveSearch = config.getboolean('Configuration', 'case_sensitive')
	useSQLButtons = config.getboolean('Configuration', 'use_SQL_buttons')
	showComments = config.getboolean('Configuration', 'show_comments')
	
	if config.get('Configuration', 'language') <> 'English':
		names = LANG.spanish
	else:
		names = LANG.english

		
def createConfigFile(configFileName):
	config = ConfigParser.RawConfigParser()
	config.add_section('Configuration')
	config.set('Configuration', 'pretty_print', 'True')
	config.set('Configuration', 'no_spaces_in_closed_tag', 'True')
	config.set('Configuration', 'linefy_at_save', 'True')
	config.set('Configuration', 'case_sensitive', 'False')
	config.set('Configuration', 'use_SQL_buttons', 'False')
	config.set('Configuration', 'show_comments', 'True')
	config.set('Configuration', 'language', 'Español')
	with open(configFileName, 'wb') as configfile:
		config.write(configfile)
		
def updateConfigFile(seccion, campo, valor):
	global configFileName
	config = ConfigParser.RawConfigParser()
	config.read(configFileName)
	
	config.set(seccion, campo, valor)
	with open(configFileName, 'wb') as configfile:
		config.write(configfile)