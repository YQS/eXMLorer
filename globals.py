# encoding: UTF-8

# GLOBAL VARIABLES

filename = ''
XMLTree = None
XMLParentMap = {}
dicTagsInTree = {}
appTreeView = None

buttonWidth = 15

marginToExtendToText = 30
dataColumnTextLimit = 100

fileNameDic = 'namedic'
dicTagSubnames = {}

def getDicSubnames():
	global dicTagSubnames
	with open(fileNameDic, 'r') as txt:
		sDic = txt.read()
		if sDic <> '':
			dicNames = eval(sDic)
		else:
			dicNames = {}
	#return dicNames
	dicTagSubnames = dicNames
	
def setDicSubnames():
	global dicTagSubnames
	with open(fileNameDic, 'w') as txt:
		txtDic = repr(dicTagSubnames).replace(',' , ',\n\r')
		txt.write(txtDic)
